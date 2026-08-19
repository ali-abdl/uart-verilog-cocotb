import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

from scoreboard import Scoreboard

CLKS_PER_BIT = 32
CLK_PERIOD_NS = 20


async def reset_dut(dut):
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


async def send(dut, value):
    """Hand a byte to the transmitter once it's free."""
    while dut.tx_busy.value == 1:
        await RisingEdge(dut.clk)

    dut.tx_data.value = value
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0


async def rx_monitor(dut, sb):
    """Feed every byte the receiver reports into the scoreboard."""
    while True:
        await RisingEdge(dut.clk)
        if dut.rx_valid.value == 1:
            if dut.rx_frame_error.value == 1:
                sb.errors += 1
                sb.log.error("framing error on a loopback frame")
            sb.check(int(dut.rx_data.value))


@cocotb.test()
async def test_loopback_single(dut):
    """One byte makes the full round trip."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    sb = Scoreboard(dut._log, name="loopback")
    cocotb.start_soon(rx_monitor(dut, sb))

    sb.expect(0xA5)
    await send(dut, 0xA5)

    for _ in range(20 * CLKS_PER_BIT):
        if sb.checked == 1:
            break
        await RisingEdge(dut.clk)

    assert sb.checked == 1, "byte never came back"
    assert sb.errors == 0, "round trip corrupted the byte"
    dut._log.info("0xA5 survived the round trip")


@cocotb.test()
async def test_loopback_random(dut):
    """Random bytes with random gaps, TX -> wire -> RX."""
    N = 100

    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    sb = Scoreboard(dut._log, name="loopback")
    cocotb.start_soon(rx_monitor(dut, sb))

    for _ in range(N):
        value = random.randint(0, 255)
        sb.expect(value)
        await send(dut, value)
        await ClockCycles(dut.clk, random.randint(1, 2 * CLKS_PER_BIT))

    for _ in range(30 * CLKS_PER_BIT):
        if sb.checked == N:
            break
        await RisingEdge(dut.clk)

    assert sb.checked == N, f"only {sb.checked}/{N} bytes made the round trip"
    assert sb.errors == 0, f"{sb.errors} scoreboard errors"
    sb.report()