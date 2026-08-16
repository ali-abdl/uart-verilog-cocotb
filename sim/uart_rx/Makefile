include ../common.mk

VERILOG_SOURCES += $(RTL)/uart_rx.v
VERILOG_SOURCES += $(RTL)/baud_gen.v

TOPLEVEL = uart_rx
MODULE   = test_uart_rx

COMPILE_ARGS += -Puart_rx.CLKS_PER_BIT=32
COMPILE_ARGS += -Puart_rx.OVERSAMPLE=16

include $(shell cocotb-config --makefiles)/Makefile.sim