.PHONY: all clean synthesis program sim

QARTUS_BIN ?= quartus
QARTUS_MAP ?= quartus_map
QARTUS_FIT ?= quartus_fit
QARTUS_ASM ?= quartus_asm
QARTUS_STA ?= quartus_sta
QARTUS_PGM ?= quartus_pgm
VSIM ?= vsim

PROJECT_NAME := cnc_fpga
FPGA_DEVICE := EP4CE6E22C8

all: synthesis

synthesis: 
	$(QUARTUS_BIN) --flow compile cnc_controller_fpga

program:
	$(QUARTUS_PGM) -c 1 -m JTAG -o "P;output_files/$(PROJECT_NAME).sof"

sim:
	cd sim && $(VSIM) -do "do wave.do"

clean:
	rm -rf db incremental_db output_files simulation
	*.jdi *.rpt *.summary *.smsg *.msg

help:
	@echo "CNC FPGA Build System"
	@echo "====================="
	@echo "make synthesis  - Synthesize and place & route design"
	@echo "make program    - Program FPGA via JTAG"
	@echo "make sim        - Run ModelSim simulation"
	@echo "make clean      - Clean build artifacts"
	@echo "make help       - Show this help message"
