
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
	
	# load_program_memory reads the input memory, and populates the instruction memory
	def load_program_memory(self, file_name):
		try:
			fp = open(file_name, 'r')
			for line in fp:
				tmp = line.split()
				if len(tmp) == 2:
					address, instruction = tmp[0], tmp[1]
					self.write_word(address, instruction)
			fp.close()
		except:
			print("ERROR: Error opening input .mc file\n")
			exit(1)

	# Memory write
	def write_word(self, address, instruction):
		idx = int(address[2:], 16)
		self.MEM[idx] =  instruction[8:10]
		self.MEM[idx + 1] = instruction[6:8]
		self.MEM[idx + 2] = instruction[4:6]
		self.MEM[idx + 3] = instruction[2:4]
  
	# Creates a "data_out.mc" file and writes the data memory in it. It also creates
	# a reg_out.mc file and writes the contents of registers in it.
	def write_data_memory(self):
		try:
			fp = open("data_out.mc", "w")
			out_tmp = []
			for i in range(268435456, 268468221, 4):
				out_tmp.append(
					hex(i) + ' 0x' + self.MEM[i + 3] + self.MEM[i + 2] + self.MEM[i + 1] + self.MEM[i] + '\n')
			fp.writelines(out_tmp)
			fp.close()
		except:
			print("ERROR: Error opening data_out.mc file for writing\n")
			exit(1)

		try:
			fp = open("reg_out.mc", "w")
			out_tmp = []
			for i in range(32):
				out_tmp.append('x' + str(i) + ' ' + self.R[i] + '\n')
			fp.writelines(out_tmp)
			fp.close()
		except:
			print("ERROR: Error opening reg_out.mc file for writing\n")
			exit(1)

	def IAG(self, state):
		if state.pc_select:
			self.next_PC = state.return_address
		elif state.inc_select:
			self.next_PC += state.pc_offset
		else:
			self.next_PC += 4

		state.pc_select = 0
		state.inc_select = 0

	# Reads from the instruction memory and updates the instruction register
	def fetch(self, state, *args):
		if state.is_dummy:
			return

		if self.all_dummy:
			state.is_dummy = True
			return

		state.instruction_word = '0x' + self.MEM[state.PC + 3] + self.MEM[state.PC + 2] + self.MEM[state.PC + 1] + self.MEM[state.PC]

		if not self.pipelining_enabled:
			return

		btb = args[0]

		if btb.find(state.PC):
			state.branch_taken = btb.predict(state.PC)
			if state.branch_taken:
				state.next_pc = btb.getTarget(state.PC)
			else:
				state.next_pc = state.PC + 4
    
    
    # Decodes the instruction and decides the operation to be performed in the execute stage; reads the operands from the register file.
	def decode(self, state, *args):
		if state.is_dummy:
			return False, 0, False, 0

		if state.instruction_word == '0x401080BB':
			self.terminate = True
			state.is_dummy = True
			self.all_dummy = True
			return False, 0, False, 0

		bin_instruction = bin(int(state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction

		opcode = int(bin_instruction[25:32], 2)
		func3 = int(bin_instruction[17:20], 2)
		func7 = int(bin_instruction[0:7], 2)

		path = os.path.dirname(__file__)
		f = open(os.path.join(path,'Instruction_Set_List.csv'))
		instruction_set_list = list(csv.reader(f))
		f.close()

		match_found = False
		track = 0

		for ins in instruction_set_list:
			if track == 0:
				match_found = False
			elif ins[4] != 'NA' and [int(ins[2], 2), int(ins[3], 2), int(ins[4], 2)] == [opcode, func3, func7]:
				match_found = True
			elif ins[4] == 'NA' and ins[3] != 'NA' and [int(ins[2], 2), int(ins[3], 2)] == [opcode, func3]:
				match_found = True
			elif ins[4] == 'NA' and ins[3] == 'NA' and int(ins[2], 2) == opcode:
				match_found = True
			if match_found:
				break
			track += 1

		if not match_found:
			print("ERROR: Unidentifiable machine code!\n")
			exit(1)

		op_type = instruction_set_list[track][0]
		state.alu_control_signal = track

		state.is_mem = [-1, -1]

		if op_type == 'R':
			state.rs2 = bin_instruction[7:12]
			state.rs1 = bin_instruction[12:17]
			state.rd = bin_instruction[20:25]
			state.operand1 = self.R[int(state.rs1, 2)]
			state.operand2 = self.R[int(state.rs2, 2)]
			state.write_back_signal = True

		elif op_type == 'I':
			state.rs1 = bin_instruction[12:17]
			state.rd = bin_instruction[20:25]
			imm = bin_instruction[0:12]
			if not state.decode_forwarding_op1:
				state.operand1 = self.R[int(state.rs1, 2)]
			state.operand2 = imm
			state.write_back_signal = True

		elif op_type == 'S':
			state.rs2 = bin_instruction[7:12]
			state.rs1 = bin_instruction[12:17]
			imm = bin_instruction[0:7] + bin_instruction[20:25]
			if not state.decode_forwarding_op1:
				state.operand1 = self.R[int(state.rs1, 2)]
			state.operand2 = imm
			state.register_data = self.R[int(state.rs2, 2)]
			state.write_back_signal = False

		elif op_type == 'SB':
			state.rs2 = bin_instruction[7:12]
			state.rs1 = bin_instruction[12:17]
			if not state.decode_forwarding_op1:
				state.operand1 = self.R[int(state.rs1, 2)]
			if not state.decode_forwarding_op2:
				state.operand2 = self.R[int(state.rs2, 2)]
			imm = bin_instruction[0] + bin_instruction[24] + \
				bin_instruction[1:7] + bin_instruction[20:24] + '0'
			state.offset = imm
			state.write_back_signal = False

		elif op_type == 'U':
			state.rd = bin_instruction[20:25]
			imm = bin_instruction[0:20] + '0'*12
			state.write_back_signal = True
			state.operand2 = imm

		elif op_type == 'UJ':
			state.rd = bin_instruction[20:25]
			imm = bin_instruction[0] + bin_instruction[12:20] + \
				bin_instruction[11] + bin_instruction[1:11] + '0'
			state.write_back_signal = True
			state.offset = imm

		else:
			print("ERROR: Unidentifiable machine code!\n")
			exit(1)

		if self.pipelining_enabled:
			branch_ins = [23, 24, 25, 26, 29, 19]
			entering = False

			if state.alu_control_signal not in branch_ins:
				return False, 0, entering, 0

			else:
				self.execute(state)
				self.next_PC = state.PC
				self.IAG(state)
				orig_pc = self.next_PC
				btb = args[0]

				if btb.find(state.PC) and orig_pc != state.next_pc:
					self.count_branch_mispredictions += 1


				if not btb.find(state.PC):
					state.inc_select = self.inc_select
					state.pc_select = self.pc_select
					state.pc_offset = self.pc_offset
					state.return_address = self.return_address
					self.next_PC = state.PC
					self.IAG(state)
					state.pc_update = self.next_PC
					if state.alu_control_signal == 19 or state.alu_control_signal == 29:
						btb.enter(True, state.PC, state.pc_update)
					else:
						btb.enter(False, state.PC, state.pc_update)
						# entering = True if jalr is always green
					self.reset()
					self.reset(state)
					entering = True

				if orig_pc != state.next_pc:
					return True, orig_pc, entering, 1
				else:
					return False, 0, entering, 3 # 0: no_pred, 1: wrong, 3: correct