#!/usr/bin/env python3
"""
Cortex Session Startup — run at every session start.
Prints structured bootstrap instructions for Claude to execute.

Usage: python ~/.claude/skills/cortex/bin/startup.py [--mode coding|research|review|quick]
"""

import argparse
import sys
import io
from datetime import datetime, date
from pathlib import Path

# Fix Unicode output on Windows cp1252 consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

INTERVALS = {
    "coding": 10,
    "research": 20,
    "review": 30,
    "quick": 0,
}

def check_healthcheck_needed():
    """Check if healthcheck should run (first session today)."""
    marker = Path.home() / ".claude" / "cortex-last-health"
    today = date.today().isoformat()
    if marker.exists():
        last = marker.read_text().strip()
        if last == today:
            return False
    marker.write_text(today)
    return True

def main():
    parser = argparse.ArgumentParser(description="Cortex session startup")
    parser.add_argument("--mode", choices=INTERVALS.keys(), default="coding",
                        help="Work mode for heartbeat interval")
    args = parser.parse_args()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"=== CORTEX BOOTSTRAP ({now}) ===")
    print()

    # Step 1: Orphan cron cleanup
    print("STEP 1 — CLEAN ORPHAN CRONS:")
    print("  CronList → delete any with 'Cortex heartbeat' in prompt")
    print()

    # Step 2: Heartbeat
    interval = INTERVALS[args.mode]
    if interval > 0:
        print(f"STEP 2 — SET HEARTBEAT ({args.mode} mode, {interval}min):")
        print(f"  CronCreate(interval={interval}min, prompt='Cortex heartbeat: ...')")
    else:
        print("STEP 2 — SKIP HEARTBEAT (quick question mode)")
    print()

    # Step 3: Healthcheck
    needs_health = check_healthcheck_needed()
    if needs_health:
        print("STEP 3 — HEALTHCHECK (first session today):")
        print("  python ~/.claude/skills/cortex/bin/healthcheck.py")
    else:
        print("STEP 3 — SKIP HEALTHCHECK (already ran today)")
    print()

    print("=== BOOTSTRAP READY ===")

if __name__ == "__main__":
    main()
