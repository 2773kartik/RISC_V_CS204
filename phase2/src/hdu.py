class HDU:
	# If forwarding is not enabled
	def data_hazard_stalling(self, pipeline_instructions):
		count_data_hazard = 0
		data_hazard = False

		# since we don't have values for instruction in decode stage
		decode_state = pipeline_instructions[-2]
		bin_instruction = bin(int(decode_state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction
		decode_opcode = int(bin_instruction[25:32], 2)
		if decode_opcode in [19, 103, 3]:
			decode_state.rs1 = bin_instruction[12:17]
			decode_state.rs2 = -1
		elif decode_opcode not in [23, 55, 111]:
			decode_state.rs1 = bin_instruction[12:17]
			decode_state.rs2 = bin_instruction[7:12]

		states_to_check = pipeline_instructions[:-1]
		gui_pair = {'who': -1, 'from_whom': -1}

		exe_state = states_to_check[-2]
		decode_state = states_to_check[-1]
		if exe_state.rd != -1 and exe_state.rd != '00000' and not exe_state.is_dummy and not decode_state.is_dummy:
			if exe_state.rd == decode_state.rs1 or exe_state.rd == decode_state.rs2:
				data_hazard = True
				count_data_hazard += 1
				gui_pair = {'who': 3, 'from_whom': 2}

		mem_state = states_to_check[-3]
		if mem_state.rd != -1 and mem_state.rd != '00000' and not mem_state.is_dummy and not decode_state.is_dummy:
			if mem_state.rd == decode_state.rs1 or mem_state.rd == decode_state.rs2:
				data_hazard = True
				count_data_hazard += 1
				gui_pair = {'who': 3, 'from_whom': 1}

		return [data_hazard, count_data_hazard, gui_pair]

	# If forwarding is enabled
	def data_hazard_forwarding(self, pipeline_instructions):
		decode_state = pipeline_instructions[-2]
		exe_state = pipeline_instructions[-3]
		mem_state = pipeline_instructions[-4]
		wb_state = pipeline_instructions[-5]

		# since we don't have values for instruction in decode stage
		bin_instruction = bin(int(decode_state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction
		decode_opcode = int(bin_instruction[25:32], 2)
		if decode_opcode in [19, 103, 3]:
			decode_state.rs1 = bin_instruction[12:17]
			decode_state.rs2 = -1
		elif decode_opcode not in [23, 55, 111]:
			decode_state.rs1 = bin_instruction[12:17]
			decode_state.rs2 = bin_instruction[7:12]

		data_hazard = 0
		if_stall = False
		stall_position = 2
		gui_pair = {'who': -1, 'from_whom': -1}
		# codes for gui_for wb = 0, mem = 1, execute = 2, decode = 3, fetch = 4
		gui_for = [""]*5

		# getting opcodes
		bin_instruction = bin(int(exe_state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction
		exe_opcode = int(bin_instruction[25:32], 2)

		bin_instruction = bin(int(mem_state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction
		mem_opcode = int(bin_instruction[25:32], 2)

		bin_instruction = bin(int(wb_state.instruction_word[2:], 16))[2:]
		bin_instruction = (32 - len(bin_instruction)) * '0' + bin_instruction
		wb_opcode = int(bin_instruction[25:32], 2)

		# M -> M forwarding
		if wb_opcode == 3 and mem_opcode == 35 and not wb_state.is_dummy and not mem_state.is_dummy: # 3 == load and 35 == store
			if wb_state.rd != -1 and wb_state.rd != '00000' and wb_state.rd == mem_state.rs2:
				mem_state.register_data = wb_state.register_data
				data_hazard += 1
				gui_pair = {'who': -1, 'from_whom': -1}
				gui_for[1] = "forwarded from mem"

		# M -> E forwarding
		if wb_state.rd != -1 and wb_state.rd != '00000' and not wb_state.is_dummy:
			if wb_state.rd == exe_state.rs1 and not exe_state.is_dummy:
				exe_state.operand1 = wb_state.register_data
				data_hazard += 1
				gui_pair = {'who': -1, 'from_whom': -1}
				gui_for[2] = "forwarded from mem"

			if wb_state.rd == exe_state.rs2 and not exe_state.is_dummy:
				if exe_opcode != 35: # store
					exe_state.operand2 = wb_state.register_data
				else:
					exe_state.register_data = wb_state.register_data
				data_hazard += 1
				gui_pair = {'who': -1, 'from_whom': -1}
				gui_for[2] = "forwarded from mem"

		# E -> E forwarding
		if mem_state.rd != -1 and mem_state.rd != '00000' and not mem_state.is_dummy:
			if mem_opcode == 3: # load
				if exe_opcode == 35: # store
					if exe_state.rs1 == mem_state.rd and not exe_state.is_dummy:
						data_hazard += 1
						if_stall = True
						stall_position = 0
						gui_pair = {'who': 2, 'from_whom': 1}

				else:
					if (exe_state.rs1 == mem_state.rd or exe_state.rs2 == mem_state.rd) and not exe_state.is_dummy:
						data_hazard += 1
						if_stall = True
						stall_position = 0
						gui_pair = {'who': 2, 'from_whom': 1}

			else:
				if exe_state.rs1 == mem_state.rd and not exe_state.is_dummy:
					exe_state.operand1 = mem_state.register_data
					data_hazard += 1
					gui_pair = {'who': -1, 'from_whom': -1}
					gui_for[2] = "forwarded from execute"

				if exe_state.rs2 == mem_state.rd and not exe_state.is_dummy:
					if exe_opcode != 35: # store
						exe_state.operand2 = mem_state.register_data
					else:
						exe_state.register_data = mem_state.register_data
					data_hazard += 1
					gui_pair = {'who': -1, 'from_whom': -1}
					gui_for[2] = "forwarded from execute"

		if (decode_opcode == 99 or decode_opcode == 103) and not decode_state.is_dummy: # SB and jalr
			# M -> D forwarding
			if wb_state.rd != -1 and wb_state.rd != '00000' and not wb_state.is_dummy:
				if wb_state.rd == decode_state.rs1:
					decode_state.operand1 = wb_state.register_data
					decode_state.decode_forwarding_op1 = True
					data_hazard += 1
					gui_pair = {'who': -1, 'from_whom': -1}
					gui_for[3] = "forwarded from mem"

				if wb_state.rd == decode_state.rs2:
					decode_state.operand2 = wb_state.register_data
					decode_state.decode_forwarding_op2 = True
					data_hazard += 1
					gui_pair = {'who': -1, 'from_whom': -1}
					gui_for[3] = "forwarded from mem"

			# E -> D fowarding
			if mem_state.rd != -1 and mem_state.rd != '00000' and not mem_state.is_dummy:
				if mem_opcode == 3 and (mem_state.rd == decode_state.rs1 or mem_state.rd == decode_state.rs2): # load
					data_hazard += 1
					if_stall = True
					if stall_position > 1:
						stall_position = 1
						gui_pair = {'who': 3, 'from_whom': 1}

				else:
					if mem_state.rd == decode_state.rs1:
						decode_state.operand1 = mem_state.register_data
						decode_state.decode_forwarding_op1 = True
						data_hazard += 1
						gui_pair = {'who': -1, 'from_whom': -1}
						gui_for[3] = "forwarded from execute"

					if mem_state.rd == decode_state.rs2:
						decode_state.operand2 = mem_state.register_data
						decode_state.decode_forwarding_op2 = True
						data_hazard += 1
						gui_pair = {'who': -1, 'from_whom': -1}
						gui_for[3] = "forwarded from execute"

			# If control instruction depends on the previous instruction
			if exe_state.rd != -1 and exe_state.rd != '00000' and (exe_state.rd == decode_state.rs1 or exe_state.rd == decode_state.rs2) and not exe_state.is_dummy:
				data_hazard += 1
				if_stall = True
				if stall_position > 1:
					stall_position = 1
					gui_pair = {'who': 3, 'from_whom': 2}

		gui_pair['from'] = gui_for
		new_states = [wb_state, mem_state, exe_state, decode_state, pipeline_instructions[-1]]
		return [data_hazard, if_stall, stall_position, new_states, gui_pair]