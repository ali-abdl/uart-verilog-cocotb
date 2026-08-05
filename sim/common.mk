SIM ?= icarus
TOPLEVEL_LANG ?= verilog

RTL := $(PWD)/../../rtl
TB  := $(PWD)/../../tb

export PYTHONPATH := $(TB):$(PYTHONPATH)

VERILOG_SOURCES += $(TB)/dump.v
COMPILE_ARGS += -s dump