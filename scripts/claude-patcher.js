#!/usr/bin/env node
/**
 * Claude Code Binary Patcher
 * Auto-discovers patch points via structural pattern recognition.
 * Works across versions — finds constants by code structure, not variable names.
 *
 * Usage:
 *   node claude-patcher.js [options]
 *
 * Options:
 *   --context-window <N>     Set context window size (6 digits, e.g. 262000)
 *   --max-output <N>         Set max output token upper limit (6 digits)
 *   --autocompact-buffer <N> Set autocompact buffer (5 digits)
 *   --summary-max <N>        Set max autocompact summary tokens (5 digits)
 *   --all                    Apply all patches with defaults
 *   --scan                   Show all discovered constants (no patching)
 *   --restore                Restore from backup
 *   --dry-run                Preview patches without writing
 *   --binary <path>          Path to claude binary (auto-detected)
 *   --help                   Show this help
 *
 * Examples:
 *   node claude-patcher.js --scan
 *   node claude-patcher.js --all
 *   node claude-patcher.js --context-window 300000
 *   node claude-patcher.js --restore
 */

const fs = require("fs");
const path = require("path");

// ─── CLI ────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const getArg = (name) => { const i = args.indexOf(`--${name}`); return i === -1 ? undefined : args[i + 1]; };
const hasFlag = (name) => args.includes(`--${name}`);

if (hasFlag("help") || args.length === 0) {
  const src = fs.readFileSync(__filename, "utf8").split("\n");
  const s = src.findIndex(l => l.includes("* Usage:"));
  const e = src.findIndex((l, i) => i > s && l.includes("*/"));
  console.log(src.slice(s, e).map(l => l.replace(/^\s*\*\s?/, "")).join("\n"));
  process.exit(0);
}

// ─── Find binary ────────────────────────────────────────────────────
function findBinary() {
  const home = process.env.HOME || process.env.USERPROFILE;
  const candidates = [
    getArg("binary"),
    path.join(home, ".local", "bin", "claude.exe"),
    path.join(home, ".local", "bin", "claude"),
  ].filter(Boolean);
  for (const p of candidates) if (fs.existsSync(p)) return p;
  try {
    const { execSync } = require("child_process");
    const cmd = process.platform === "win32" ? "where claude" : "which claude";
    const r = execSync(cmd, { encoding: "utf8" }).trim().split("\n")[0];
    if (r && fs.existsSync(r)) return r;
  } catch {}
  return null;
}

const TARGET = findBinary();
if (!TARGET) { console.error("ERROR: Cannot find claude binary. Use --binary <path>"); process.exit(1); }
const BACKUP = TARGET + ".bak";
const applyAll = hasFlag("all");

// ─── Helpers ────────────────────────────────────────────────────────
function findAll(buf, pat) {
  const b = typeof pat === "string" ? Buffer.from(pat) : pat;
  const r = []; let i = 0;
  while ((i = buf.indexOf(b, i)) !== -1) { r.push(i); i++; }
  return r;
}

function strAt(buf, offset, len) {
  return buf.slice(offset, Math.min(buf.length, offset + len)).toString("utf8");
}

function strBefore(buf, offset, len) {
  return buf.slice(Math.max(0, offset - len), offset).toString("utf8");
}

// ─── Auto-Discovery ─────────────────────────────────────────────────
function discover(buf) {
  const found = {};

  // ── 1. CONTEXT WINDOW ──
  // Strategy: find "function Tv(" → extract the default return variable name
  //           → find "var VARNAME=NNNNNN," → that's the context window default
  {
    const tvMatches = findAll(buf, "function Tv(");
    for (const tvOff of tvMatches) {
      const body = strAt(buf, tvOff, 400);
      // Tv returns 1e6 for special cases, then "return VARNAME" as default
      // Find the last "return VARNAME}" — that's the default fallback
      const retMatch = body.match(/return\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\}/);
      if (!retMatch) continue;
      const varName = retMatch[1];

      // Now find where this variable is declared: "var VARNAME=NNNNNN,"
      const declPat = `var ${varName}=`;
      const declMatches = findAll(buf, declPat);
      for (const declOff of declMatches) {
        const after = strAt(buf, declOff + declPat.length, 20);
        const valMatch = after.match(/^(\d{6}),/);
        if (valMatch) {
          const value = parseInt(valMatch[1], 10);
          const fullPattern = `${varName}=${valMatch[1]},`;
          found.contextWindow = {
            name: "Context window default",
            varName,
            currentValue: value,
            pattern: fullPattern,
            occurrences: findAll(buf, fullPattern).length,
          };
          break;
        }
      }
      if (found.contextWindow) break;
    }
  }

  // ── 2. MAX OUTPUT TOKENS ──
  // Strategy: find 'includes("opus-4-6"))' followed by VAR=DIGITS,VAR=DIGITS
  //           This is the S6H function's model-specific branch
  {
    found.maxOutput = {};
    const models = [
      { search: 'includes("opus-4-6"))', label: "opus-4-6" },
      { search: 'includes("sonnet-4-6"))', label: "sonnet-4-6" },
    ];
    for (const { search, label } of models) {
      const matches = findAll(buf, search);
      for (const off of matches) {
        const after = strAt(buf, off + search.length, 60);
        // Match: $=NNNNN,q=NNNNNN or similar VAR=DIGITS,VAR=DIGITS
        const m = after.match(/^([a-zA-Z_$][a-zA-Z0-9_$]*)=(\d+),([a-zA-Z_$][a-zA-Z0-9_$]*)=(\d+)/);
        if (m) {
          const [, dVar, dVal, uVar, uVal] = m;
          const fullPattern = `${search}${dVar}=${dVal},${uVar}=${uVal}`;
          found.maxOutput[label] = {
            name: `Max output (${label})`,
            defaultVar: dVar, defaultValue: parseInt(dVal, 10),
            upperVar: uVar, upperValue: parseInt(uVal, 10),
            pattern: fullPattern,
            occurrences: findAll(buf, fullPattern).length,
          };
          break; // take first code match, skip dupes
        }
      }
    }
    if (Object.keys(found.maxOutput).length === 0) delete found.maxOutput;
  }

  // ── 3. AUTOCOMPACT BUFFER ──
  // Strategy: find the autocompact threshold function.
  // It calculates: effectiveWindow - BUFFER. The buffer var is assigned
  // in a cluster with warning (20000), error (20000), and blocking (3000) thresholds.
  // We find the cluster by locating multiple =20000, assignments near =3000,
  // then identify the buffer as the remaining 5-digit constant in that cluster.
  {
    // Find clusters: look for =20000, and check if =3000, is nearby
    const markers = findAll(buf, "=20000,");
    const seen = new Set();
    for (const mOff of markers) {
      const clusterStart = Math.max(0, mOff - 200);
      const ctx = strAt(buf, clusterStart, 500);
      if (!ctx.includes("=3000,")) continue;

      // Parse all VAR=DIGITS, in this cluster
      const re = /([a-zA-Z_$][a-zA-Z0-9_$]*)=(\d+),/g;
      let m;
      const entries = [];
      while ((m = re.exec(ctx)) !== null) {
        entries.push({ varName: m[1], value: parseInt(m[2], 10) });
      }

      // The buffer is the unique 5-digit value that isn't 20000 or 3000
      // and is in the range 5000-30000 (reasonable for a token buffer)
      const twentyKCount = entries.filter(e => e.value === 20000).length;
      const threeKCount = entries.filter(e => e.value === 3000).length;
      if (twentyKCount < 2 || threeKCount < 1) continue; // not the right cluster

      const bufferEntry = entries.find(e =>
        e.value !== 20000 && e.value !== 3000 &&
        e.value >= 5000 && e.value <= 30000 &&
        !seen.has(e.varName)
      );
      if (!bufferEntry) continue;

      const fullPattern = `${bufferEntry.varName}=${bufferEntry.value},`;
      found.autocompactBuffer = {
        name: "Autocompact buffer",
        varName: bufferEntry.varName,
        currentValue: bufferEntry.value,
        pattern: fullPattern,
        occurrences: findAll(buf, fullPattern).length,
      };

      // Collect other thresholds in cluster
      found.thresholds = [];
      for (const e of entries) {
        if (e.varName === bufferEntry.varName) continue;
        let label = "unknown";
        if (e.value === 20000) label = "warning/error threshold";
        else if (e.value === 3000) label = "blocking limit";
        else if (e.value <= 5) label = "max failures/min messages";
        else if (e.value >= 1000000) label = "cooldown (ms)";
        else if (e.value === 8000) label = "narrow mode output cap";
        found.thresholds.push({ varName: e.varName, value: e.value, label });
      }
      break;
    }
  }

  // ── 4. SUMMARY MAX TOKENS ──
  // Strategy: find the compact summary config object.
  // It has the structure: {minTokens:X,minTextBlockMessages:N,maxTokens:NNNNN}
  // We find it by locating "minTextBlockMessages:" — a unique key name —
  // then parse the surrounding object to extract maxTokens value.
  {
    const matches = findAll(buf, "minTextBlockMessages:");
    for (const off of matches) {
      const ctx = strAt(buf, off - 80, 200);
      // Match the full config object regardless of specific values
      const m = ctx.match(/minTokens:([^,]+),minTextBlockMessages:(\d+),maxTokens:(\d+)/);
      if (m) {
        const maxVal = parseInt(m[3], 10);
        const pattern = `minTextBlockMessages:${m[2]},maxTokens:${m[3]}`;
        found.summaryMax = {
          name: "Summary max tokens",
          currentValue: maxVal,
          minTokens: m[1],
          minMessages: parseInt(m[2], 10),
          pattern,
          fullObjectPattern: `minTokens:${m[1]},${pattern}`,
          occurrences: findAll(buf, pattern).length,
        };
        break;
      }
    }
  }

  // ── 5. OTHER USEFUL CONSTANTS (scan-only) ──
  // Default output tokens (xJ7), fallback upper limit (mJ7)
  {
    if (found.contextWindow) {
      // These are declared right after context window var
      const declPat = `${found.contextWindow.pattern}`;
      const matches = findAll(buf, declPat);
      if (matches.length > 0) {
        const after = strAt(buf, matches[0] + declPat.length, 200);
        found.relatedConstants = [];
        const re = /([a-zA-Z_$][a-zA-Z0-9_$]*)=(\d+)/g;
        let m;
        while ((m = re.exec(after)) !== null) {
          const [, v, n] = m;
          const num = parseInt(n, 10);
          let label = `${num}`;
          if (num === 20000) label = "output token reserve cap";
          else if (num === 32000) label = "fallback default output";
          else if (num === 64000) label = "fallback upper limit / escalation";
          else if (num === 8000) label = "narrow mode output cap";
          found.relatedConstants.push({ varName: v, value: num, label });
          if (found.relatedConstants.length >= 6) break;
        }
      }
    }
  }

  return found;
}

// ─── Build Patches ──────────────────────────────────────────────────
function buildPatches(d) {
  const patches = [];

  // Context window
  const ctxArg = getArg("context-window") || (applyAll ? "262000" : null);
  if (ctxArg) {
    const val = parseInt(ctxArg, 10);
    if (!d.contextWindow) { console.error("ERROR: Context window constant not found in binary."); process.exit(1); }
    if (isNaN(val) || String(val).length !== String(d.contextWindow.currentValue).length) {
      console.error(`ERROR: --context-window must be ${String(d.contextWindow.currentValue).length} digits`);
      process.exit(1);
    }
    if (val === d.contextWindow.currentValue) {
      console.log(`Context window already ${val}, skipping.`);
    } else {
      patches.push({
        name: `Context window: ${d.contextWindow.currentValue} -> ${val}`,
        find: Buffer.from(d.contextWindow.pattern),
        replace: Buffer.from(`${d.contextWindow.varName}=${val},`),
      });
    }
  }

  // Max output
  const moArg = getArg("max-output");
  if (moArg) {
    const val = parseInt(moArg, 10);
    if (!d.maxOutput) { console.error("ERROR: Max output constants not found in binary."); process.exit(1); }
    for (const [label, info] of Object.entries(d.maxOutput)) {
      const oldUpper = String(info.upperValue);
      if (String(val).length !== oldUpper.length) {
        console.error(`ERROR: --max-output must be ${oldUpper.length} digits to patch ${label}`);
        process.exit(1);
      }
      if (val === info.upperValue) {
        console.log(`Max output (${label}) already ${val}, skipping.`);
      } else {
        patches.push({
          name: `Max output (${label}): ${info.upperValue} -> ${val}`,
          find: Buffer.from(info.pattern),
          replace: Buffer.from(info.pattern.replace(oldUpper, String(val))),
        });
      }
    }
  }

  // Autocompact buffer
  const abArg = getArg("autocompact-buffer");
  if (abArg) {
    const val = parseInt(abArg, 10);
    if (!d.autocompactBuffer) { console.error("ERROR: Autocompact buffer not found in binary."); process.exit(1); }
    const oldStr = String(d.autocompactBuffer.currentValue);
    if (String(val).length !== oldStr.length) {
      console.error(`ERROR: --autocompact-buffer must be ${oldStr.length} digits`);
      process.exit(1);
    }
    if (val === d.autocompactBuffer.currentValue) {
      console.log(`Autocompact buffer already ${val}, skipping.`);
    } else {
      patches.push({
        name: `Autocompact buffer: ${d.autocompactBuffer.currentValue} -> ${val}`,
        find: Buffer.from(d.autocompactBuffer.pattern),
        replace: Buffer.from(`${d.autocompactBuffer.varName}=${val},`),
      });
    }
  }

  // Summary max
  const smArg = getArg("summary-max");
  if (smArg) {
    const val = parseInt(smArg, 10);
    if (!d.summaryMax) { console.error("ERROR: Summary max not found in binary."); process.exit(1); }
    const oldStr = String(d.summaryMax.currentValue);
    if (String(val).length !== oldStr.length) {
      console.error(`ERROR: --summary-max must be ${oldStr.length} digits`);
      process.exit(1);
    }
    if (val === d.summaryMax.currentValue) {
      console.log(`Summary max already ${val}, skipping.`);
    } else {
      const oldPat = d.summaryMax.pattern;
      const newPat = oldPat.replace(String(d.summaryMax.currentValue), String(val));
      patches.push({
        name: `Summary max: ${d.summaryMax.currentValue} -> ${val}`,
        find: Buffer.from(oldPat),
        replace: Buffer.from(newPat),
      });
    }
  }

  return patches;
}

// ─── Apply Patches ──────────────────────────────────────────────────
function applyPatches(buf, patches) {
  const dryRun = hasFlag("dry-run");
  let total = 0;

  for (const patch of patches) {
    console.log(`--- ${patch.name} ---`);

    const already = findAll(buf, patch.replace);
    if (already.length > 0) {
      console.log(`  Already applied (${already.length}x)\n`);
      continue;
    }

    const hits = findAll(buf, patch.find);
    if (hits.length === 0) {
      console.error(`  WARNING: Pattern not found\n`);
      continue;
    }

    let count = 0;
    for (const off of hits) {
      if (patch.contextCheck) {
        const ctx = strAt(buf, off - 200, 400 + patch.find.length);
        if (!ctx.includes(patch.contextCheck)) {
          console.log(`  Offset ${off}: context mismatch, skipping`);
          continue;
        }
      }
      if (dryRun) {
        console.log(`  [DRY] Would patch at offset ${off}`);
      } else {
        patch.replace.copy(buf, off);
        console.log(`  Patched at offset ${off}`);
      }
      count++;
    }
    console.log(`  ${count}/${hits.length} ${dryRun ? "found" : "patched"}\n`);
    total += count;
  }
  return total;
}

// ─── Main ───────────────────────────────────────────────────────────
(function main() {
  console.log("=== Claude Code Binary Patcher ===");
  console.log(`Binary: ${TARGET}`);
  console.log(`Size:   ${(fs.statSync(TARGET).size / 1e6).toFixed(1)} MB\n`);

  // Restore
  if (hasFlag("restore")) {
    if (!fs.existsSync(BACKUP)) { console.error("No backup at", BACKUP); process.exit(1); }
    try { fs.copyFileSync(BACKUP, TARGET); console.log("Restored from backup."); }
    catch (e) { if (e.code === "EBUSY") console.log("Binary locked — close Claude first."); else throw e; }
    return;
  }

  const buf = fs.readFileSync(TARGET);
  console.log("Discovering constants...\n");
  const d = discover(buf);

  // Scan mode
  if (hasFlag("scan")) {
    console.log("=== Discovered Constants ===\n");

    const show = (label, obj) => {
      if (!obj) { console.log(`${label}: NOT FOUND\n`); return; }
      console.log(`${label}:`);
      if (obj.varName) console.log(`  Variable:  ${obj.varName}`);
      console.log(`  Value:     ${obj.currentValue}`);
      console.log(`  Pattern:   ${obj.pattern}`);
      console.log(`  Found:     ${obj.occurrences}x\n`);
    };

    show("Context Window", d.contextWindow);
    show("Autocompact Buffer", d.autocompactBuffer);
    show("Summary Max Tokens", d.summaryMax);

    if (d.maxOutput) {
      for (const [label, info] of Object.entries(d.maxOutput)) {
        console.log(`Max Output (${label}):`);
        console.log(`  Default:   ${info.defaultVar}=${info.defaultValue}`);
        console.log(`  Upper:     ${info.upperVar}=${info.upperValue}`);
        console.log(`  Pattern:   ${info.pattern}`);
        console.log(`  Found:     ${info.occurrences}x\n`);
      }
    } else {
      console.log("Max Output: NOT FOUND\n");
    }

    if (d.thresholds?.length) {
      console.log("Threshold Cluster:");
      for (const t of d.thresholds) console.log(`  ${t.varName}=${t.value} (${t.label})`);
      console.log();
    }

    if (d.relatedConstants?.length) {
      console.log("Related Constants (near context window):");
      for (const c of d.relatedConstants) console.log(`  ${c.varName}=${c.value} (${c.label})`);
      console.log();
    }

    return;
  }

  // Build & apply
  const patches = buildPatches(d);
  if (patches.length === 0) { console.log("Nothing to patch. Use --help for options."); process.exit(0); }

  if (!fs.existsSync(BACKUP)) {
    console.log("Backup ->", BACKUP);
    fs.copyFileSync(TARGET, BACKUP);
  } else {
    console.log("Backup at", BACKUP);
  }
  console.log();

  const total = applyPatches(buf, patches);

  if (hasFlag("dry-run")) { console.log(`Dry run: ${total} patch point(s).`); return; }
  if (total === 0) { console.log("No new patches applied."); process.exit(0); }

  // Write
  const TEMP = TARGET + ".patched";
  let writtenTo;
  try {
    fs.writeFileSync(TARGET, buf);
    writtenTo = TARGET;
    console.log(`Written -> ${TARGET}`);
  } catch (e) {
    if (e.code === "EBUSY" || e.code === "EPERM") {
      fs.writeFileSync(TEMP, buf);
      writtenTo = TEMP;
      console.log(`Locked. Written -> ${TEMP}`);
      console.log(`\nClose Claude, then:`);
      console.log(process.platform === "win32"
        ? `  Copy-Item -Force "${TEMP}" "${TARGET}"`
        : `  cp "${TEMP}" "${TARGET}"`);
    } else throw e;
  }

  // Verify
  console.log("\n=== Verify ===");
  const v = fs.readFileSync(writtenTo);
  for (const p of patches) {
    const ok = findAll(v, p.replace).length > 0;
    console.log(`[${ok ? "OK" : "FAIL"}] ${p.name}`);
  }
  console.log(`\nRestore: node ${__filename} --restore`);
})();
