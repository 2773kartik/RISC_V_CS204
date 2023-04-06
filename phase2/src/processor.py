
from collections import defaultdict
from sys import exit

class Processor:
	def __init__(self, file_name):
		self.MEM = defaultdict(lambda: '00')
		self.R = ['0x00000000' for i in range(32)]
		self.R[2] = '0x7FFFFFF0'
		self.R[3] = '0x10000000'
		self.load_program_memory(file_name)
		self.pipelining_enabled = False
		self.terminate = False
		self.next_PC = 0
		self.inc_select = 0
		self.pc_select = 0
		self.return_address = -1
		self.pc_offset = 0
		# Various Counts
		self.count_total_inst = 0
		self.count_alu_inst = 0
		self.count_mem_inst = 0
		self.count_control_inst = 0
		self.count_branch_mispredictions = 0
		self.all_dummy = False
		# gui variable
		self.get_code = defaultdict(lambda: -1)

	def reset(self, *args):
		if len(args) > 0:
			state = args[0]
			state.inc_select = 0
			state.pc_select = 0
			state.pc_offset = 0
			state.return_address = 0

		else:
			self.inc_select = 0
			self.pc_select = 0
			self.pc_offset = 0
			self.return_address = 0