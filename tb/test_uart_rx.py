import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

CLKS_PER_BIT = 32
CLK_PERIOD_NS = 20


async def reset_dut(dut):
    """Idle the line high, then reset."""
    dut.rx_serial.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


async def uart_send(dut, value, stop_bit=1):
    """Drive one UART frame onto rx_serial, LSB first."""
    dut.rx_serial.value = 0                        # start bit
    await ClockCycles(dut.clk, CLKS_PER_BIT)

    for i in range(8):
        dut.rx_serial.value = (value >> i) & 1     # data bits
        await ClockCycles(dut.clk, CLKS_PER_BIT)

    dut.rx_serial.value = stop_bit                 # stop bit (0 = framing error)
    await ClockCycles(dut.clk, CLKS_PER_BIT)

    dut.rx_serial.value = 1                        # return to idle


async def wait_for_byte(dut, timeout_bits=15):
    """Wait for rx_valid; return (data, frame_error)."""
    for _ in range(timeout_bits * CLKS_PER_BIT):
        await RisingEdge(dut.clk)
        if dut.rx_valid.value == 1:
            return int(dut.rx_data.value), int(dut.rx_frame_error.value)
    raise AssertionError("timed out waiting for rx_valid")


@cocotb.test()
async def test_single_byte(dut):
    """Receive 0xA5 cleanly."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    cocotb.start_soon(uart_send(dut, 0xA5))
    data, err = await wait_for_byte(dut)

    assert data == 0xA5, f"expected 0xA5, got 0x{data:02X}"
    assert err == 0, "unexpected framing error"
    dut._log.info(f"received 0x{data:02X}")


@cocotb.test()
async def test_patterns(dut):
    """Byte patterns that stress bit ordering and flat runs."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, units="ns").start())
    await reset_dut(dut)

    for value in (0x01, 0x80, 0x0F, 0xF0, 0x00, 0xFF, 0x5A):
        cocotb.start_soon(uart_send(dut, value))
        data, err = await wait_for_byte(dut)
        assert data == value, f"sent 0x{value:02X}, got 0x{data:02X}"
        assert err == 0, f"framing error on 0x{value:02X}"
        dut._log.info(f"ok: 0x{value:02X}")
        await ClockCycles(dut.clk, CLKS_PER_BIT)