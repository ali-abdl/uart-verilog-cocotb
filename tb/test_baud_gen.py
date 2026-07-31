import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge

DIVISOR = 4

@cocotb.test()
async def test_tick_period(dut):
    """tick should pulse for one cycle, once every DIVISOR clock cycles."""

    # start a free running 50mhz clock ( 20 ns period) on dut.clk
    cocotb.start_soon(Clock(dut.clk,20, units="ns").start())

    # assert reset, hold it two cycles then release
    dut.rst_n.value=0
    dut.en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value =1
    dut.en.value = 1 

    # align ourselves, advance until we see the first tick
    await FallingEdge(dut.clk)
    while dut.tick.value == 0:
        await FallingEdge(dut.clk)

    # measure how many cycles until next one
    gap = 0
    while True:
        await FallingEdge(dut.clk)
        gap += 1
        if dut.tick.value == 1:
            break

    assert gap == DIVISOR, f"expected a tick every {DIVISOR} cycles, measured {gap}"
    dut._log.info(f"PASS: tick period measured as {gap} cycles")

@cocotb.test()
async def test_disabled_holds_low(dut):
    """With en low, tick must never fire."""

    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    dut.rst_n.value = 0
    dut.en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1

    for _ in range(4 * DIVISOR):
        await FallingEdge(dut.clk)
        assert dut.tick.value == 0, "tick fired while disabled"