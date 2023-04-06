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
