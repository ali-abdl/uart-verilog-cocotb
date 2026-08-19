include ../common.mk

VERILOG_SOURCES += $(TB)/uart_loopback.v
VERILOG_SOURCES += $(RTL)/uart.v
VERILOG_SOURCES += $(RTL)/uart_tx.v
VERILOG_SOURCES += $(RTL)/uart_rx.v
VERILOG_SOURCES += $(RTL)/baud_gen.v

TOPLEVEL = uart_loopback
MODULE   = test_loopback

COMPILE_ARGS += -Puart_loopback.CLKS_PER_BIT=32
COMPILE_ARGS += -Puart_loopback.OVERSAMPLE=16

include $(shell cocotb-config --makefiles)/Makefile.sim