include ../common.mk

VERILOG_SOURCES += $(RTL)/uart_tx.v
VERILOG_SOURCES += $(RTL)/baud_gen.v

TOPLEVEL = uart_tx
MODULE   = test_uart_tx

COMPILE_ARGS += -Puart_tx.CLKS_PER_BIT=8

include $(shell cocotb-config --makefiles)/Makefile.sim