#include<map>
#include<vector>
#include<string>
#include<algorithm>
extern long reg[32];
extern long RS1,RS2,RD,RM,RZ,RY,RA,RB,PC,IR,MuxB_select,MuxC_select,MuxINC_select,MuxY_select,MuxPC_select,MuxMA_select,RegFileAddrA,RegFileAddrB,RegFileAddrC,RegFileInp,RegFileAOut,RegFileBOut,MAR,MDR,opcode,numBytes,RF_Write,immed,PC_Temp,Mem_Write,Mem_Read;
extern long ALU[15];
extern long ui, clk;
extern long stepClick;
extern std::map<int, std::vector<int>> dataMemory;
extern std::map<int, std::vector<int>> instructionMemory;

void init() {
    for(auto &i : ALU) i = 0;
    for(auto &i : reg) i = 0;
    reg[2] = 0x7FFFFFF0;    //sp -> Stack polonger
    reg[3] = 0x10000000;    //data pointer
    RS1 = RS2 = RD = RM = RZ = RY = RA = RB = PC = IR = MuxB_select = MuxC_select = MuxINC_select = MuxY_select = MuxPC_select = MuxMA_select = RegFileAddrA = RegFileAddrB = RegFileAddrC = RegFileInp = RegFileAOut = RegFileBOut = MAR = MDR = opcode = numBytes = RF_Write = immed = PC_Temp = Mem_Write = Mem_Read = 0;
}

std::string hex(long n) {
    
}

void ProcessMemInterface() {
    if(MuxMA_select == 0) {
        if(Mem_Read==1) {
            std::vector<int> t;
            for(int i = 0; i < numBytes; ++i) {
                t.push_back(dataMemory[MAR][i]);
            }
            reverse(t.begin(), t.end());
            std::string ans = "0x";
        }
    }
}


void GenerateControlSignals(int reg_write,int MuxB,int MuxY,int MemRead,int MemWrite,int MuxMA,int MuxPC,int MuxINC,int numB){

}


// ---------------------------------------------FLOWCHART---------------------------------------------//
/*          
                                                R TYPE

OPCODE          func3           func7       Instruction
0110011          0x0            0x00            add
0110011          0x0            0x20            sub
0110011          0x0            0x01            mul

0110011          0x7            0x00            and

0110011          0x6            0x00            or
0110011          0x6            0x01            rem

0110011          0x1            0x00            sll

0110011          0x2            0x00            slt

0110011          0x5            0x00            srl
0110011          0x5            0x20            sra

0110011          0x4            0x00            xor
0110011          0x4            0x01            div

                                                I TYPE

OPCODE          func3           Instruction
0000011          0x0                lb
0000011          0x1                lh
0000011          0x2                lw

0010011          0x0                addi
0010011          0x7                andi
0010011          0x6                ori


1100111          0x0                jalr

                                                S TYPE

OPCODE          func3           Instruction
0100011          0x0                sb
0100011          0x1                sh
0100011          0x2                sw

*/

// ---------------------------------------------------------------------------------------------------//

int ALUOp[15];

void Decode() {

    for(int &i : ALUOp) i = 0; 

    int func3, func7;
    std::string message = "";

    opcode = IR & 0x7f;                     // Finding Opcode
    func3 = (IR & 0x7000) >> 12;            // Finding Func3


    if(opcode == 51){
        // R Format
        GenerateControlSignals(1,0,0,0,0,0,1,0,4);
        RD = (IR & 0xF80) >> 7;             // Setting destination register
        RS1 = (IR & 0xF8000) >> 15;         // Setting Source1 Register
        RS2 = (IR & 0x1F00000) >> 20;       // Setting Source2 Register
        func7 = (IR & 0xFE000000) >> 25;    // Setting Func7

        if(func3 == 0x0){   // add/sub/mul
            if(func7 == 0x00){ 
                // add Instruction 
                ALUOp[0] = 1;
                message = "This is Add Instruction.";
            }
            else if(func7 == 0x20){
                // subtract Instruction
                ALUOp[1] = 1;
                message = "This is Sub Instruction.";
            }
            else if(func7 == 0x01){
                // multiply Instruction
                ALUOp[3] = 1;
                message = "This is Mul Instruction.";
            }
            else{
                cout << "Invalid Func7 for Add/Sub/Mul";
                return;
            }
        }
        else if(func3 == 0x7){  // and
            if(func7 == 0x00){
                // and Instruction
                message = "This is AND Instruction.";
                ALUOp[10] = 1;
            }
            else{
                cout << "Invalid Func7 for And";
                return;
            }
        }
        else if(func3 == 0x6){  // or/rem
            if(func7 == 0x00){
                // or Instruction
                message = "This is OR Instruction.";
                ALUOp[9] = 1;
            }
            else if(func7 == 0x01){
                // rem Instruction
                message = "This is Rem Instruction.";
                ALUOp[4] = 1;
            }
            else{
                cout << "Invalid Func7 for Or/Rem.";
                return;
            }
        }
        else if(func3 == 0x1){  // sll
            if(func7 == 0x00){
                // sll Instruction
                message = "This is SLL Instruction.";
                ALUOp[6] = 1;
            }
            else{
                cout << "Invalid Func7 for SLL";
                return;
            }
        }
        else if(func3 == 0x2){  // slt
            if(func7 == 0x00){
                // slt Instruciton
                message = "This is SLT Instruction.";
                ALUOp[11] = 1;
            }
            else{
                cout << "Invalid Func7 for SLT";
                return;
            }
        }
        else if(func3 == 0x5){  // srl/sra
            if(func7 == 0x00){
                // srl Instruction
                message = "This is SRL Instruction.";
                ALUOp[8] = 1;
            }
            else if(func7 == 0x20){
                // sra Instruction
                message = "This is SRA Instruction.";
                ALUOp[7] = 1;
            }
            else{
                cout << "Invalid Instruction for SRA/SRL.";
                return;
            }
        }
        else if(func3 == 0x4){  // xor/div
            if(func7 == 0x00){
                // xor Instruction
                message = "This is XOR Instruction.";
                ALUOp[5] = 1;
            }
            else if(func7 == 0x01){
                // div Instruction
                message = "This is DIV Instruction.";
                ALUOp[2] = 1;
            }
            else{
                cout << "Invalid func7 fro XOR/DIV.";
                return;
            }
        }
        else{
            cout << "Func3 not matching in R format";
            return;
        }

        RA = reg[RS1];      // Setting RA
        RB = reg[RS2];      // Setting RB
        RM = RB;            // Setting RM

    }
    else if(opcode == 19 || opcode == 3 || opcode == 103){  // I Format
        
        RD = (IR & 0xF80) >> 7;             // Setting Destination Register
        RS1 = (IR & 0xF8000) >> 15;         // Setting Source1 Register
        immed = (IR & 0xFFF00000) >> 20;    // Setting Immediate value

        if(immed > 2047) immed -= 4096;     // Constraint on Immediate

        if(opcode == 3){    // lb/lh/lw
            ALUOp[0] = 1;
            if(func3 == 0x0){
                // lb Instruction
                message = "This is Lb Instruction.";
                GenerateControlSignals(1,1,1,1,0,0,1,0,1);
            }
            else if(func3 == 0x1){ 
                // lh Instruction 
                message = "This is Lh Instruction.";
                GenerateControlSignals(1,1,1,1,0,0,1,0,2);
            }
            else if(func3 == 0x2){
                // lw Instruction
                message = "This is Lw Instruction.";
                GenerateControlSignals(1,1,1,1,0,0,1,0,4);
            }
            else{
                cout << "Invalid func3 for lb/lw/lh.";
                return;
            }

            RA = reg[RS1];      // Setting RA
            // RB and RM are don't cares    
        }
        else if(opcode == 19){  // addi/andi/ori
            GenerateControlSignals(1,1,0,0,0,0,1,0,4);
            if(func3 == 0x0){
                // addi Instruction
                message = "This is addi Instruction.";
                ALUOp[0] = 1;
            }
            else if(func3 == 0x7){
                // andi Instruction
                message = "This is andi Instruction.";
                ALUOp[10] = 1;
            }
            else if(func3 == 0x6){
                // ori Instruction
                message = "This is ori Instruction.";
                ALUOp[9] = 1;
            }
            else{
                cout << "Invalid func3 for addi/andi/ori";
                return;
            }

            RA = reg[RS1];
        }
        else if(opcode == 103){ // jalr
            message = "This is JALR Instruction.";
            GenerateControlSignals(1,0,2,0,0,0,0,1,4);
            if(func3 == 0x0){
                // jalr instrucition
                ALUOp[0] = 1;
            }
            else{
                cout << "Invalid func3 for jalr.";
                return;
            }

            RA = reg[RS1];      // Setting RA
            // RB and RM are DON"T CARES
        }
    }
    else if(opcode == 35){  // S Format

        RS1 = (IR & 0xF8000) >> 15;                 // Setting Source1 Register
        RS2 = (IR & 0x1F00000) >> 20;               // Setting Source2 Register
        int immed_4to0 = (IR & 0xF80) >> 7;         // Extracting immediate[4:0]
        int immed_11to5 = (IR & 0xFE000000) >> 25;  // Extracting immediate[11:5]
        immed = immed_4to0 | immed_11to5;           // Setting immediate
        // ImmediateSign(12);  
        ALUOp[0] = 1;
        if(func3 == 0x0){
            // sb Instruction
            message = "This is sb Instruction.";
            GenerateControlSignals(0,1,1,0,1,0,1,0,1);
        }
        else if(func3 == 0x1){
            // sh Instruction
            message = "This is sh Instruction.";
            GenerateControlSignals(0,1,1,0,1,0,1,0,2);
        }
        else if(func3 == 0x2){
            // sw Instruction
            message = "This is sw Instruction.";
            GenerateControlSignals(0,1,1,0,1,0,1,0,4);
        }
        else{
            cout << "Invalid func3 for sb/sh/sw";
            return;
        }

        RA = reg[RS2];      // Setting RA
        RB = reg[RS1];      // Setting RB
        RM = RB;            // Setting RM
    }
}