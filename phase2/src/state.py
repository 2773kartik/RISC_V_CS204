# Instruction/State Class
class State:
	def __init__(self, pc = 0):
		self.PC = pc
		self.instruction_word = '0x0'
		self.rs1 = -1
		self.rs2 = -1
		self.operand1 = 0
		self.operand2 = 0
		self.rd = -1
		self.offset = 0
		self.register_data = '0x00000000'
		self.memory_address = 0
		self.alu_control_signal = -1
		self.is_mem = [-1, -1] # [-1/0/1(no memory operation/load/store), type of load/store if any]
		self.write_back_signal = False
		#
		self.is_dummy = False
		self.pc_update = -1
		self.branch_taken = False
		#
		self.inc_select = 0
		self.pc_select = 0
		self.pc_offset = 0
		self.return_address = -1
		self.next_pc = -1
		#
		self.decode_forwarding_op1 = False
		self.decode_forwarding_op2 = False
		self.asm_code = ''