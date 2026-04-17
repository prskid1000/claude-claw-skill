"""claw web fetch — HTTP GET/POST with cookies, headers, retries."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, safe_write,
)

DEFAULT_UA = "claw/1.0 (+https://github.com/anthropic/claude-claw)"


def _parse_kv_pair(items: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for it in items:
        if "=" not in it:
            raise click.BadParameter(f"expected K=V, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


def _resolve_data(data: str | None) -> bytes | None:
    if data is None:
        return None
    if data.startswith("@"):
        return Path(data[1:]).read_bytes()
    return data.encode("utf-8")


@click.command(name="fetch")
@click.argument("url")
@click.option("--out", default=None, type=click.Path(path_type=Path),
              help="Output file or `-` for stdout (default: stdout).")
@click.option("--method", default="GET",
              type=click.Choice(["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"],
                                case_sensitive=False))
@click.option("--header", "headers", multiple=True, metavar="K=V",
              help="Request header (repeatable).")
@click.option("--data", default=None, help="Request body. Prefix @ to load from file.")
@click.option("--timeout", default=30.0, type=float, help="Seconds (default 30).")
@click.option("--retries", default=0, type=int, help="Retries on 5xx / transient errors.")
@click.option("--follow-redirects/--no-follow-redirects", default=True)
@click.option("--max-redirects", default=20, type=int)
@click.option("--save-cookies", default=None, type=click.Path(path_type=Path))
@click.option("--load-cookies", default=None, type=click.Path(path_type=Path, exists=True))
@click.option("--ua", default=DEFAULT_UA, help="User-Agent string.")
@click.option("--proxy", default=None, help="Proxy URL.")
@click.option("--accept-errors", is_flag=True, help="Don't exit non-zero on HTTP >= 400.")
@common_output_options
def fetch(url: str, out: Path | None, method: str, headers: tuple[str, ...],
          data: str | None, timeout: float, retries: int, follow_redirects: bool,
          max_redirects: int, save_cookies: Path | None, load_cookies: Path | None,
          ua: str, proxy: str | None, accept_errors: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """HTTP GET/POST a URL; write body to --out or stdout."""
    try:
        import httpx
    except ImportError:
        die("httpx not installed", code=EXIT_INPUT,
            hint="pip install 'claw[web]'", as_json=as_json)

    try:
        hdrs = _parse_kv_pair(headers)
    except click.BadParameter as e:
        die(str(e), code=EXIT_INPUT, as_json=as_json)
    hdrs.setdefault("User-Agent", ua)
    body = _resolve_data(data)

    cookies = None
    if load_cookies:
        from http.cookiejar import MozillaCookieJar
        jar = MozillaCookieJar(str(load_cookies))
        jar.load(ignore_discard=True, ignore_expires=True)
        cookies = jar

    if dry_run:
        if as_json:
            emit_json({"would_fetch": url, "method": method.upper(), "headers": hdrs})
        else:
            click.echo(f"would {method.upper()} {url}")
        return

    client = httpx.Client(
        follow_redirects=follow_redirects, max_redirects=max_redirects,
        timeout=timeout, proxy=proxy, cookies=cookies,
    )
    attempt = 0
    start = time.monotonic()
    try:
        while True:
            try:
                resp = client.request(method.upper(), url, headers=hdrs, content=body)
                if resp.status_code >= 500 and attempt < retries:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                break
            except httpx.HTTPError as e:
                if attempt < retries:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                die(f"network error: {e}", code=EXIT_SYSTEM, as_json=as_json)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        if save_cookies:
            from http.cookiejar import MozillaCookieJar
            jar = MozillaCookieJar(str(save_cookies))
            for c in client.cookies.jar:
                jar.set_cookie(c)
            jar.save(ignore_discard=True, ignore_expires=True)

        content = resp.content
        if out is None or str(out) == "-":
            sys.stdout.buffer.write(content)
            body_path = None
        else:
            safe_write(out, lambda f: f.write(content),
                       force=force, backup=backup, mkdir=mkdir)
            body_path = str(out)

        if as_json:
            emit_json({
                "url": url, "status": resp.status_code, "final_url": str(resp.url),
                "headers": dict(resp.headers), "body_path": body_path,
                "size": len(content), "elapsed_ms": elapsed_ms,
            })
        elif not quiet and body_path:
            click.echo(f"{resp.status_code} {resp.reason_phrase} -> {body_path} ({len(content)} bytes, {elapsed_ms}ms)",
                       err=True)

        if resp.status_code >= 400 and not accept_errors:
            sys.exit(6)
    finally:
        client.close()
