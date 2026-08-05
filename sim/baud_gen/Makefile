include ../common.mk

VERILOG_SOURCES += $(RTL)/baud_gen.v

TOPLEVEL = baud_gen
MODULE   = test_baud_gen

COMPILE_ARGS += -Pbaud_gen.DIVISOR=4

include $(shell cocotb-config --makefiles)/Makefile.sim