from collections import defaultdict
from sys import exit
import os
import csv
from utility import nhex, nint, sign_extend

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
				

	def execute(self, state):
		if state.is_dummy:
			return

		if state.alu_control_signal == 2:
			state.register_data = nhex(int(nint(state.operand1, 16) + nint(state.operand2, 16)))
			state.asm_code = "add x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 8:
			state.register_data = nhex(int(nint(state.operand1, 16) - nint(state.operand2, 16)))
			state.asm_code = "sub x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 1:
			state.register_data = nhex(int(int(state.operand1, 16) & int(state.operand2, 16)))
			state.asm_code = "and x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 3:
			state.register_data = nhex(int(int(state.operand1, 16) | int(state.operand2, 16)))
			state.asm_code = "or x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 4:
			if(nint(state.operand2, 16) < 0):
				print("ERROR: Shift by negative!\n")
				exit(1)
			else:
				state.register_data = nhex(int(int(state.operand1, 16) << int(state.operand2, 16)))
			state.asm_code = "sll x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 5:
			if (nint(state.operand1, 16) < nint(state.operand2, 16)):
				state.register_data = hex(1)
			else:
				state.register_data = hex(0)
			state.asm_code = "slt x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 6:
			if(nint(state.operand2, 16) < 0):
				print("ERROR: Shift by negative!\n")
				exit(1)
			else:
				state.register_data = bin(int(int(state.operand1, 16) >> int(state.operand2, 16)))
				if state.operand1[2] == '8' or state.operand1[2] == '9' or state.operand1[2] == 'a' or state.operand1[2] == 'b' or state.operand1[2] == 'c' or state.operand1[2] == 'd' or state.operand1[2] == 'e' or state.operand1[2] == 'f':
					state.register_data = '0b' + (34 - len(state.register_data)) * '1' + state.register_data[2:]
				state.register_data = hex(int(state.register_data, 2))
			state.asm_code = "sra x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 7:
			if(nint(state.operand2, 16) < 0):
				print("ERROR: Shift by negative!\n")
				exit(1)
			else:
				state.register_data = nhex(int(state.operand1, 16) >> int(state.operand2, 16))
			state.asm_code = "srl x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 9:
			state.register_data = nhex(int(int(state.operand1, 16) ^ int(state.operand2, 16)))
			state.asm_code = "xor x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 10:
			state.register_data = nhex(int(nint(state.operand1, 16) * nint(state.operand2, 16)))
			state.asm_code = "mul x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 11:
			if nint(state.operand2, 16) == 0:
				print("ERROR: Division by zero!\n")
				exit(1)
			else:
				state.register_data = nhex(int(nint(state.operand1, 16) / nint(state.operand2, 16)))
			state.asm_code = "div x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 12:
			state.register_data = nhex(int(nint(state.operand1, 16) % nint(state.operand2, 16)))
			state.asm_code = "rem x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2))

		elif state.alu_control_signal == 14:
			state.register_data = nhex(
				int(nint(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2))))
			state.asm_code = "addi x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1,2)) + " " + str(nint(state.operand2, 2, len(state.operand2)))

		elif state.alu_control_signal == 13:
			state.register_data = nhex(int(int(state.operand1, 16) & int(state.operand2, 2)))
			state.asm_code = "andi x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " " + str(int(state.operand2, 2))

		elif state.alu_control_signal == 15:
			state.register_data = nhex(int(int(state.operand1, 16) | int(state.operand2, 2)))
			state.asm_code = "ori x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " " + str(int(state.operand2, 2))

		elif state.alu_control_signal == 16:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [0, 0]
			state.asm_code = "lb x" + str(int(state.rd, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1,2)) + ")"

		elif state.alu_control_signal == 17:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [0, 1]
			state.asm_code = "lh x" + str(int(state.rd, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1,2)) + ")"

		elif state.alu_control_signal == 18:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [0, 3]
			state.asm_code = "lw x" + str(int(state.rd, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1,2)) + ")"

		elif state.alu_control_signal == 19: # Jalr
			state.register_data = nhex(state.PC + 4)
			self.return_address = nint(state.operand2, 2, len(state.operand2)) + nint(state.operand1, 16)
			self.pc_select = 1
			state.pc_select = 1
			state.return_address = nint(state.operand2, 2, len(state.operand2)) + nint(state.operand1, 16)
			state.asm_code = "jalr x" + str(int(state.rd, 2)) + " x" + str(int(state.rs1, 2)) + " " + str(nint(state.operand2, 2, len(state.operand2)))

		elif state.alu_control_signal == 20:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [1, 0]
			state.asm_code = "sb x" + str(int(state.rs2, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1, 2)) + ")"

		elif state.alu_control_signal == 22:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [1, 1]
			state.asm_code = "sh x" + str(int(state.rs2, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1, 2)) + ")"

		elif state.alu_control_signal == 21:
			state.memory_address = int(int(state.operand1, 16) + nint(state.operand2, 2, len(state.operand2)))
			state.is_mem = [1, 3]
			state.asm_code = "sw x" + str(int(state.rs2, 2)) + ' ' + str(nint(state.operand2, 2, len(state.operand2))) + " (x" + str(int(state.rs1, 2)) + ")"

		elif state.alu_control_signal == 23:
			if nint(state.operand1, 16) == nint(state.operand2, 16):
				state.pc_offset = nint(state.offset, 2, len(state.offset))
				state.inc_select = 1
			self.pc_offset = nint(state.offset, 2, len(state.offset))
			self.inc_select = 1
			state.asm_code = "beq x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2)) + " " + str(self.pc_offset)

		elif state.alu_control_signal == 24:
			if nint(state.operand1, 16) != nint(state.operand2, 16):
				state.pc_offset = nint(state.offset, 2, len(state.offset))
				state.inc_select = 1
			self.pc_offset = nint(state.offset, 2, len(state.offset))
			self.inc_select = 1
			state.asm_code = "bne x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2)) + " " + str(self.pc_offset)

		elif state.alu_control_signal == 25:
			if nint(state.operand1, 16) >= nint(state.operand2, 16):
				state.pc_offset = nint(state.offset, 2,  len(state.offset))
				state.inc_select = 1
			self.pc_offset = nint(state.offset, 2,  len(state.offset))
			self.inc_select = 1
			state.asm_code = "bge x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2)) + " " + str(self.pc_offset)

		elif state.alu_control_signal == 26:
			if nint(state.operand1, 16) < nint(state.operand2, 16):
				state.pc_offset =  nint(state.offset, 2, len(state.offset))
				state.inc_select = 1
			self.pc_offset =  nint(state.offset, 2, len(state.offset))
			self.inc_select = 1
			state.asm_code = "blt x" + str(int(state.rs1, 2)) + " x" + str(int(state.rs2, 2)) + " " + str(self.pc_offset)

		elif state.alu_control_signal == 27:
			state.register_data = nhex(int(state.PC + 4 + int(state.operand2, 2)))
			state.asm_code = "auipc x" + str(int(state.rd, 2)) + " " + str(int(state.operand2[:20], 2))

		elif state.alu_control_signal == 28:
			state.register_data = nhex(int(state.operand2, 2))
			state.asm_code = "lui x" + str(int(state.rd, 2)) + " " + str(int(state.operand2[:20], 2))

		elif state.alu_control_signal == 29: # Jal
			state.register_data = nhex(state.PC + 4)
			self.pc_offset = nint(state.offset, 2, len(state.offset))
			self.inc_select = 1
			state.pc_offset = nint(state.offset, 2, len(state.offset))
			state.inc_select = 1
			state.asm_code = "jal x" + str(int(state.rd, 2)) + " " + str(self.pc_offset)

		self.get_code[state.PC] = state.asm_code

		if len(state.register_data) > 10:
			state.register_data = state.register_data[:2] + state.register_data[-8:]

		state.register_data = state.register_data[:2] + \
			(10 - len(state.register_data)) * '0' + state.register_data[2::]
		
	# Performs the memory operations
	def mem(self, state):
		if not self.pipelining_enabled:
			self.IAG(state)

		if state.is_dummy:
			return

		if state.is_mem[0] == -1:
			return

		elif state.is_mem[0] == 0:
			state.register_data = '0x'
			if state.is_mem[1] == 0:
				state.register_data += self.MEM[state.memory_address]
			elif state.is_mem[1] == 1:
				state.register_data += (self.MEM[state.memory_address + 1] + self.MEM[state.memory_address])
			else:
				state.register_data += (self.MEM[state.memory_address + 3] + self.MEM[state.memory_address + 2] + self.MEM[state.memory_address + 1] + self.MEM[state.memory_address])

			state.register_data = sign_extend(state.register_data)

		else:
			if state.is_mem[1] >= 3:
				self.MEM[state.memory_address + 3] = state.register_data[2:4]
				self.MEM[state.memory_address + 2] = state.register_data[4:6]
			if state.is_mem[1] >= 1:
				self.MEM[state.memory_address + 1] = state.register_data[6:8]
			if state.is_mem[1] >= 0:
				self.MEM[state.memory_address] = state.register_data[8:10]
    
    # Writes the results back to the register file
	def write_back(self, state):
		if not state.is_dummy:
			self.count_total_inst += 1 # total instructions

			if state.alu_control_signal in [19, 23, 24, 25, 26, 29]:  # control instruction
				self.count_control_inst += 1

			elif state.alu_control_signal in [16, 17, 18, 20, 21, 22]: # data transfer instruction
				self.count_mem_inst += 1

			else:
				self.count_alu_inst += 1 # alu instruction

			if state.write_back_signal:
				if int(state.rd, 2) != 0:
					self.R[int(state.rd, 2)] = state.register_data