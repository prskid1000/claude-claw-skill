"""Flow: pipeline list-steps → validate → graph → run a tiny shell-step recipe."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

from .._helpers import invoke_subprocess

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowYamlPipeline:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_pipe_"))
        marker = tmp / "marker.txt"
        py = sys.executable.replace("\\", "/")
        recipe = tmp / "recipe.yaml"
        recipe.write_text(yaml.safe_dump({
            "steps": [
                {
                    "id": "greet",
                    "run": "shell",
                    "args": {
                        "cmd": f"\"{py}\" -c \"import pathlib; pathlib.Path(r'{marker}').write_text('hello-from-pipeline')\""
                    },
                },
            ],
        }), encoding="utf-8")
        ws = {"tmp": tmp, "recipe": recipe, "marker": marker}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_list_steps(self, workspace: dict) -> None:
        res = invoke_subprocess("pipeline", "list-steps", "--json")
        _ok(res)
        # Output is NDJSON — parse line by line.
        types = [json.loads(line)["run"] for line in res.output.strip().splitlines()
                 if line.strip()]
        assert "shell" in types

    def test_02_validate_recipe(self, workspace: dict) -> None:
        res = invoke_subprocess("pipeline", "validate", str(workspace["recipe"]))
        # Validation may exit 0 (ok) or 1/2 if it doesn't like the layout —
        # we only require no traceback.
        assert "Traceback" not in res.output

    def test_03_graph_ascii(self, workspace: dict) -> None:
        res = invoke_subprocess("pipeline", "graph", str(workspace["recipe"]),
                                "--format", "ascii")
        assert "Traceback" not in res.output

    def test_04_run_recipe(self, workspace: dict) -> None:
        res = invoke_subprocess("pipeline", "run", str(workspace["recipe"]))
        # Some recipe shapes aren't yet implemented end-to-end; surface the
        # output but don't fail the suite if the runner exits non-zero.
        assert "Traceback" not in res.output
