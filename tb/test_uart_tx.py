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


@cocotb.test()
async def test_single_byte(dut):
    """Transmit 0xA5 and decode it back off the wire."""

    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    assert dut.tx_serial.value == 1, "line should idle high"

    # Start the receiver model BEFORE kicking off the transmission
    rx_task = cocotb.start_soon(uart_receive(dut))

    dut.tx_data.value = 0xA5
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0

    await rx_task
    received = rx_task.result()

    assert received == 0xA5, f"expected 0xA5, got 0x{received:02X}"
    dut._log.info(f"correctly received 0x{received:02X}")