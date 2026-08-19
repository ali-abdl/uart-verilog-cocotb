import random
from scoreboard import Scoreboard
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

CLKS_PER_BIT = 8
CLK_PERIOD_NS = 20


async def reset_dut(dut):
    """Put the DUT into a known state."""
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def uart_receive(dut):
    """Behavioural UART receiver: decode one frame off tx_serial."""

    # Wait for the start bit (line goes 1 -> 0)
    await FallingEdge(dut.tx_serial)

    # Move to the middle of the start bit
    await ClockCycles(dut.clk, CLKS_PER_BIT // 2)
    assert dut.tx_serial.value == 0, "start bit was not low at its centre"

    # Sample the 8 data bits, LSB first
    byte = 0
    for i in range(8):
        await ClockCycles(dut.clk, CLKS_PER_BIT)
        byte |= int(dut.tx_serial.value) << i

    # Stop bit
    await ClockCycles(dut.clk, CLKS_PER_BIT)
    assert dut.tx_serial.value == 1, "stop bit was not high"

    return byte

async def send_and_receive(dut, value):
    """Transmit one byte and return what a receiver would decode."""
    rx_task = cocotb.start_soon(uart_receive(dut))

    dut.tx_data.value = value
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0

    await rx_task

    # Wait for the transmitter to finish the stop bit and return to idle
    while dut.tx_busy.value == 1:
        await RisingEdge(dut.clk)

    return rx_task.result()

@cocotb.test()
async def test_single_byte(dut):
    """Transmit 0xA5 and decode it back off the wire."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    assert dut.tx_serial.value == 1, "line should idle high"

    got = await send_and_receive(dut, 0xA5)
    assert got == 0xA5, f"expected 0xA5, got 0x{got:02X}"


@cocotb.test()
async def test_bit_order_and_patterns(dut):
    """Bytes chosen to expose bit-ordering and stuck-bit bugs."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    for value in (0x01, 0x80, 0x0F, 0xF0, 0x00, 0xFF):
        got = await send_and_receive(dut, value)
        assert got == value, f"sent 0x{value:02X}, got back 0x{got:02X}"
        dut._log.info(f"ok: 0x{value:02X}")


@cocotb.test()
async def test_busy_and_done_handshake(dut):
    """tx_busy spans the frame; tx_done pulses exactly once, at the end."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    assert dut.tx_busy.value == 0, "busy should be low when idle"

    dut.tx_data.value = 0x5A
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0

    await FallingEdge(dut.clk)
    assert dut.tx_busy.value == 1, "busy should assert once transmitting"

    done_pulses = 0
    for _ in range(CLKS_PER_BIT * 12):
        await FallingEdge(dut.clk)
        if dut.tx_done.value == 1:
            done_pulses += 1
            assert dut.tx_busy.value == 0, "busy must drop when done pulses"

    assert done_pulses == 1, f"expected exactly 1 done pulse, got {done_pulses}"


async def tx_monitor(dut, scoreboard):
    """Runs forever, decoding every frame that appears on the wire."""
    while True:
        byte = await uart_receive(dut)
        scoreboard.check(byte)


async def drive_byte(dut, value):
    """Wait until the transmitter is free, then start a frame."""
    while dut.tx_busy.value == 1:
        await RisingEdge(dut.clk)

    dut.tx_data.value = value
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0

@cocotb.test()
async def test_randomized(dut):
    """send many random bytes with random idle gaps; scoreboard checks them all"""
    N = 200

    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units = "ns").start())
    await reset_dut(dut)

    sb = Scoreboard(dut._log)
    cocotb.start_soon(tx_monitor(dut,sb))

    for _ in range (N):
        value = random.randint(0,255)
        sb.expect(value)
        await drive_byte(dut, value)
        await ClockCycles(dut.clk, random.randint(1,3* CLKS_PER_BIT))

    # let the final frame drain, with a timeout so a lost byte fails instead of hanging
    for _ in range (20*CLKS_PER_BIT):
        if sb.checked == N:
            break
        await RisingEdge(dut.clk)

    assert sb.checked == N, f"only {sb.checked} / {N} bytes reached the scoreboard"
    assert sb.errors == 0, f"{sb.errors} scoreboard errors"
    dut._log.info(f"scoreboard: {sb.checked} bytes checked, 0 mismatches")