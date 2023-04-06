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