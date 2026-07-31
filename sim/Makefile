SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# the rl we're testing
VERILOG_SOURCES += $(PWD)/../rtl/baud_gen.v 

# name of the verilog module to instantiate as the top level

TOPLEVEL = baud_gen

# name of the python module containing the tests, no.py extension
MODULE = test_baud_gen

# let python find the testbench folder
export PYTHONPATH := $(PWD)/../tb:$(PYTHONPATH)

# override the divisor parameter at compile time
COMPILE_ARGS += -Pbaud_gen.DIVISOR=4

VERILOG_SOURCES += $(PWD)/../tb/dump.v
COMPILE_ARGS += -s dump

include $(shell cocotb-config --makefiles)/Makefile.sim 