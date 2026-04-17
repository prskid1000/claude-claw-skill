"""Shared helpers for claw subcommands."""

from claw.common.click_ext import LazyGroup, common_output_options, help_all_option
from claw.common.errors import (
    EXIT_GENERIC, EXIT_INPUT, EXIT_INTERRUPT, EXIT_OK, EXIT_PARTIAL,
    EXIT_SYSTEM, EXIT_USAGE, die, emit_error,
)
from claw.common.geometry import Geometry
from claw.common.io import emit_json, read_bytes, read_rows, read_text, write_rows_csv, write_text
from claw.common.safe import safe_copy, safe_write
from claw.common.selectors import NodeSelector, PageSelector, RangeSelector
from claw.common.gws_util import gws_run
from claw.common.subprocess_util import require, run, run_stream, which

__all__ = [
    "LazyGroup", "common_output_options", "help_all_option",
    "EXIT_OK", "EXIT_GENERIC", "EXIT_USAGE", "EXIT_PARTIAL", "EXIT_INPUT",
    "EXIT_SYSTEM", "EXIT_INTERRUPT", "die", "emit_error",
    "Geometry",
    "emit_json", "read_text", "read_bytes", "read_rows", "write_text", "write_rows_csv",
    "safe_write", "safe_copy",
    "NodeSelector", "PageSelector", "RangeSelector",
    "gws_run",
    "require", "run", "run_stream", "which",
]
