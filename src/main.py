from processor import *
from state import *
from btb import *
from hdu import *

pc_tmp = []
dataHazardPairs = []
controlHazardSignals = []

def evaluate(processor, pipelineInstructions):
    processor.writeBack(pipelineInstructions[0])
    processor.MemoryAccess(pipelineInstructions[1])
    processor.execute(pipelineInstructions[2])
    controlHazard, controlPC, enter, color = processor.decode(pipelineInstructions[3], btb)
    # if(processor.terminate==True):
    #     print(f"gaand m danda de")
    #     for i in range(5):
    #         print(pipelineInstructions[i].stall)
            # pipelineInstructions[i].stall=True
    if enter:
        controlHazardSignals.append(2)
    elif pipelineInstructions[2].stall and color !=0 and len(controlHazardSignals) > 0 and controlHazardSignals[-1] == 2:
        controlHazardSignals.append(controlHazardSignals[-1])
    else:
        controlHazardSignals.append(color)
    processor.fetch(pipelineInstructions[4],btb)
    return [pipelineInstructions[1],pipelineInstructions[2],pipelineInstructions[3],pipelineInstructions[4]], controlHazard, controlPC
        

if __name__ == '__main__':
    
    file1="demofile.txt"
    knob_input=open("input.txt", "r")
    knobs=[]
    for line in knob_input:
        x=line.split()
        if x[0]=='True':
            if len(x)==1:
                knobs.append(True)
            else:
                knobs.append([True,x[1]])
        
        else:
            if len(x)==1:
                knobs.append(False)
            else:
                knobs.append([False,x[1]])

    knob_input.close()
    # Knobs
    pipelining_knob=knobs[0]  # knob1
    forwarding_knob=knobs[1]   # knob2
    print_registers_each_cycle=knobs[2]    # knob3
    print_pipeline_registers=knobs[3]   # knob4
    print_specific_pipeline_registers =knobs[4]  # knob5
    # Various Counts
    stalls_due_to_data_hazard = 0
    number_of_data_hazards = 0
    stalls_due_to_control_hazard = 0
    totalStalls = 0

    #initial calling of classes.
    processor = processor(file1)
    hdu=HDU()
    btb=BTB()

    # Signals
    PC = 0
    clock_cycles = 0
    prog_end = False

    if not pipelining_knob:

        processor.pipelingEnabled=False
        while True:

            curr_instruction=State(PC)
            processor.fetch(curr_instruction)
            clock_cycles +=1
            if print_registers_each_cycle:
                print("CLOCK CYCLE:", clock_cycles)
                print("Register Data:-")
                for i in range(32):
                    print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")
                pc_tmp.append([-1, -1, -1, -1, curr_instruction.PC])

            processor.decode(curr_instruction)
            clock_cycles +=1
            if print_registers_each_cycle:
                print("CLOCK CYCLE:", clock_cycles)
                print("Register Data:-")
                for i in range(32):
                    print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")
            pc_tmp.append([-1, -1, -1, curr_instruction.PC,-1])

            if processor.terminate:
                prog_end = True
                break
            

            processor.execute(curr_instruction)
            clock_cycles +=1
            if print_registers_each_cycle:
                print("CLOCK CYCLE:", clock_cycles)
                print("Register Data:-")
                for i in range(32):
                    print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")
            pc_tmp.append([-1, -1,curr_instruction.PC,-1,-1])

            processor.MemoryAccess(curr_instruction)
            clock_cycles +=1
            if print_registers_each_cycle:
                print("CLOCK CYCLE:", clock_cycles)
                print("Register Data:-")
                for i in range(32):
                    print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")
            pc_tmp.append([-1,curr_instruction.PC,-1,-1,-1])

            processor.writeBack(curr_instruction)
            clock_cycles +=1
            if print_registers_each_cycle:
                print("CLOCK CYCLE:", clock_cycles)
                print("Register Data:-")
                for i in range(32):
                    print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")
            pc_tmp.append([curr_instruction.PC,-1,-1,-1,-1])

            PC=processor.PC_next

    else:
        processor.pipeliningEnabled = True
        pipelineInstructions = [State(0) for x in range(5)]
        for i in range(4):
            pipelineInstructions[i].stall = True
        
        while not prog_end:
            if not forwarding_knob:
                
                dataHazard = hdu.dataHazardStalling(pipelineInstructions)

                oldStates = pipelineInstructions
                pipelineInstructions, controlHazard, controlPC = evaluate(processor, pipelineInstructions)
                
                dataHazardPairs.append(dataHazard[2])
                branch_taken = pipelineInstructions[3].branch_taken
                branch_pc = pipelineInstructions[3].PC_next

                PC += 4

                if branch_taken and not dataHazard[0]:
                    PC = branch_pc
                
                if controlHazard and not dataHazard[0]:
                    stalls_due_to_control_hazard += 1
                    PC = controlPC
                    pipelineInstructions.append(State(PC))
                    pipelineInstructions[-2].stall = True

                if dataHazard[0]:
                    number_of_data_hazards += dataHazard[1]
                    stalls_due_to_data_hazard += 1
                    pipelineInstructions = pipelineInstructions[:2] + [State(0)] + oldStates[3:]
                    pipelineInstructions[2].stall = True
                    PC -= 4
                
                if not controlHazard and not dataHazard[0]:
                    pipelineInstructions.append(State(PC))
                
                pipelineInstructions[-2].PC_next = PC

                prog_end = True
                for i in range(4):
                    x = pipelineInstructions[i]
                    if not x.stall:
                        prog_end = False
                        break

            else:
                dataHazard, ifStall, stallPos, pipelineInstructions, toFrom = hdu.dataHazardForwarding(pipelineInstructions)

                oldStates = pipelineInstructions
                pipelineInstructions, controlHazard, controlPC = evaluate(processor, pipelineInstructions)

                dataHazardPairs.append(toFrom)

                branch_taken = pipelineInstructions[3].branch_taken
                branch_pc = pipelineInstructions[3].PC_next

                PC += 4

                if branch_taken and not ifStall:
                    PC = branch_pc
                
                if controlHazard and not ifStall:
                    stalls_due_to_control_hazard += 1
                    PC = controlPC
                    pipelineInstructions.append(State(PC))
                    pipelineInstructions[-2].stall = True

                if ifStall:
                    stalls_due_to_data_hazard += 1

                    if stallPos == 0:
                        pipelineInstructions = pipelineInstructions[:1] + [State(0)] + oldStates[2:]
                        pipelineInstructions[1].stall = True
                        PC -= 4

                    elif stallPos == 1:
                        pipelineInstructions = pipelineInstructions[:2] + [State(0)] + oldStates[3:]
                        pipelineInstructions[2].stall = True
                        PC -= 4
                
                number_of_data_hazards += dataHazard

                if not controlHazard and not ifStall:
                    pipelineInstructions.append(State(PC))
                
                pipelineInstructions[-2].PC_next = PC

                for inst in pipelineInstructions:
                    inst.decode_forwarding_op1 = False
                    inst.decode_forwarding_op2 = False
                
                prog_end = True
                for i in range(4):
                    x = pipelineInstructions[i] 
                    if not x.stall:
                        prog_end = False
                        break
                
                clock_cycles += 1
                # Print the register values after each clock cycle
                if print_registers_each_cycle:
                    print("CLOCK CYCLE:", clock_cycles)
                    print("Register Data:-")
                    for i in range(32):
                        print("R" + str(i) + ":", processor.registers[i], end=" ")
                    print("\n")

                # Print specific pipeline registers
                if print_specific_pipeline_registers[0]:
                    for inst in pipelineInstructions:
                        if inst.PC/4 == print_specific_pipeline_registers[1]:
                            if not print_registers_each_cycle:
                                print("CLOCK CYCLE:", clock_cycles)
                            print("Pipeline Registers:-")
                            print("Fetch # Decode =>", "Instruction:", pipelineInstructions[3].IR)
                            print("Decode # Execute => ", "Operand1: ", pipelineInstructions[2].RA, ", Operand2: ", pipelineInstructions[2].RB, sep="")
                            print("Execute # Memory => ", "Data: ", pipelineInstructions[1].RY, sep="")
                            print("Memory # WriteBack => ", "Data: ", pipelineInstructions[0].RY, sep="")
                            print("\n")

                # Print pipeline registers
                elif print_pipeline_registers:
                    if not print_registers_each_cycle:
                        print("CLOCK CYCLE:", clock_cycles)
                        print("Pipeline Registers:-")
                        print("Fetch # Decode =>", "Instruction:", pipelineInstructions[3].IR)
                        print("Decode # Execute => ", "Operand1: ", pipelineInstructions[2].RA, ", Operand2: ", pipelineInstructions[2].RB, sep="")
                        print("Execute # Memory => ", "Data: ", pipelineInstructions[1].RY, sep="")
                        print("Memory # WriteBack => ", "Data: ", pipelineInstructions[0].RY, sep="")
                        print("\n")

    processor.writeDataMemory()