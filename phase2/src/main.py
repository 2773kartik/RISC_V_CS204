from processor import Processor
from state import State
from hdu import HDU
from btb import BTB

stats = [
	"Total number of cycles: ",
	"Total instructions executed: ",
	"CPI: ",
	"Number of data-transfer(load and store): ",
	"Number of ALU instructions executed: ",
	"Number of Control instructions: ",
	"Number of stalls/bubbles in the pipeline: ",
	"Number of data hazards: ",
	"Number of control hazards: ",
	"Number of branch mispredictions: ",
	"Number of stalls due to data hazards: ",
	"Number of stalls due to control hazards: "
]

control_hazard_signals = []

def evaluate(processor, pipeline_ins):
	processor.write_back(pipeline_ins[0])
	processor.mem(pipeline_ins[1])
	processor.execute(pipeline_ins[2])
	control_hazard, control_pc, entering, color = processor.decode(pipeline_ins[3], btb)
	if entering:
		control_hazard_signals.append(2)
	elif pipeline_ins[2].is_dummy and color != 0 and len(control_hazard_signals) > 0 and control_hazard_signals[-1] == 2:
		control_hazard_signals.append(control_hazard_signals[-1])
	else:
		control_hazard_signals.append(color)
	processor.fetch(pipeline_ins[4], btb)
	pipeline_ins = [pipeline_ins[1], pipeline_ins[2], pipeline_ins[3], pipeline_ins[4]]
	return pipeline_ins, control_hazard, control_pc

if __name__ == '__main__':

	# set .mc file and input knobs
	prog_mc_file, pipelining_enabled, forwarding_enabled, print_registers_each_cycle, print_pipeline_registers, print_specific_pipeline_registers = take_input()

	# Knobs
	# pipelining_enabled = True                       # Knob1
	# forwarding_enabled = False                      # Knob2
	# print_registers_each_cycle = False              # Knob3
	# print_pipeline_registers = False    			  # Knob4
	# print_specific_pipeline_registers = [False, 10] # Knob5

	# invoke classes
	processor = Processor(prog_mc_file)
	hdu = HDU()
	btb = BTB()

	# Signals
	PC = 0
	clock_cycles = 0
	prog_end = False

	# Various Counts
	number_of_stalls_due_to_control_hazards = 0
	number_of_data_hazards = 0
	number_of_stalls_due_to_data_hazards = 0
	total_number_of_stalls = 0