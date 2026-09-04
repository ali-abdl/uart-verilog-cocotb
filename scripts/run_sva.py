#!/usr/bin/env python3
"""Build and run the SystemVerilog assertion testbenches under Verilator."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "sim" / "sva_build"

SUITES = [
    {
        "name": "uart_tx",
        "top": "tb_uart_tx_sva",
        "sources": ["rtl/uart_tx.v", "rtl/baud_gen.v",
                    "sva/uart_tx_sva.sv", "sva/tb_uart_tx_sva.sv"],
    },
    {
        "name": "uart_rx",
        "top": "tb_uart_rx_sva",
        "sources": ["rtl/uart_rx.v", "rtl/baud_gen.v",
                    "sva/uart_rx_sva.sv", "sva/tb_uart_rx_sva.sv"],
    },
]


def run_suite(suite):
    """Build and run one assertion testbench; return (ok, note)."""
    mdir = BUILD / suite["name"]
    mdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "verilator", "--binary", "--timing", "--assert",
        "--Mdir", str(mdir),
        "--top-module", suite["top"],
    ] + [str(ROOT / src) for src in suite["sources"]]

    if subprocess.run(cmd, cwd=ROOT).returncode != 0:
        return False, "verilator build failed"

    binary = mdir / f"V{suite['top']}"
    if not binary.exists():
        return False, "no simulation binary produced"

    sim = subprocess.run([str(binary)])
    if sim.returncode != 0:
        return False, f"assertion failure (exit {sim.returncode})"

    return True, None


def main():
    rows = []
    for suite in SUITES:
        print(f"\n{'=' * 60}\n  SVA: {suite['name']}\n{'=' * 60}")
        ok, note = run_suite(suite)
        rows.append((suite["name"], ok, note))

    print(f"\n{'=' * 60}\n  SVA SUMMARY\n{'=' * 60}")
    failed = 0
    for name, ok, note in rows:
        print(f"{name:<14}{'OK' if ok else f'FAILED ({note})'}")
        if not ok:
            failed += 1

    print("-" * 60)
    print(f"{len(rows) - failed}/{len(rows)} suites passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())