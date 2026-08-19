#!/usr/bin/env python3
"""Run every cocotb suite and summarise results. Exits non zero on any failure."""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUITES = ["baud_gen", "uart_tx", "uart_rx", "loopback"]


def run_suite(name):
    """Run one suite; return (passed, failed, note)."""
    sim_dir = ROOT / "sim" / name
    results = sim_dir / "results.xml"

    # Delete stale results first, so a failed build can't report an old pass
    if results.exists():
        results.unlink()

    subprocess.run(
        ["make", "clean"], cwd=sim_dir,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    proc = subprocess.run(["make"], cwd=sim_dir, check=False)

    if not results.exists():
        return 0, 1, f"no results.xml (make exited {proc.returncode})"

    passed = failed = 0
    for testcase in ET.parse(results).iter("testcase"):
        if testcase.find("failure") is not None:
            failed += 1
        else:
            passed += 1

    if passed + failed == 0:
        return 0, 1, "results.xml contained no testcases"

    return passed, failed, None


def main():
    rows = []
    for name in SUITES:
        print(f"\n{'=' * 60}\n  {name}\n{'=' * 60}")
        rows.append((name,) + run_suite(name))

    print(f"\n{'=' * 60}\n  REGRESSION SUMMARY\n{'=' * 60}")
    print(f"{'SUITE':<14}{'PASS':>6}{'FAIL':>6}  {'STATUS'}")

    total_pass = total_fail = 0
    for name, passed, failed, note in rows:
        total_pass += passed
        total_fail += failed
        status = "OK" if failed == 0 else f"FAILED ({note})" if note else "FAILED"
        print(f"{name:<14}{passed:>6}{failed:>6}  {status}")

    print("-" * 60)
    print(f"{'TOTAL':<14}{total_pass:>6}{total_fail:>6}")

    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())