#include<iostream>
#include<map>
#include<vector>
#include<string>
#include<algorithm>
extern long long  reg[32];
extern long long  RS1,RS2,RD,RM,RZ,RY,RA,RB,PC,IR,MuxB_select,MuxC_select,MuxINC_select,MuxY_select,MuxPC_select,MuxMA_select,RegFileAddrA,RegFileAddrB,RegFileAddrC,RegFileInp,RegFileAOut,RegFileBOut,MAR,MDR,opcode,numBytes,RF_Write,immed,PC_Temp,Mem_Write,Mem_Read;
extern long long  ALUOp[15];
extern long long  ui, clk;
extern long long  stepClick;
extern std::map<long long , std::vector<long long >> dataMemory;
extern std::map<long long , std::vector<std::string>> instructionMemory;

// Utility function to convert long long  integer to hexadecimal string
std::string hex(long long  n) {
    std::string ans = "";
    while (n != 0) {
        long long  rem = 0;
        char ch;
        rem = n % 16;
        if (rem < 10) {
            ch = rem + 48;
        }
        else {
            ch = rem + 55;
        }
        ans += ch;
        n = n / 16;
    }
    reverse(ans.begin(), ans.end());
    return ans;
}

void init() {
    for(auto &i : ALUOp) i = 0;
    for(auto &i : reg) i = 0;
    reg[2] = 0x7FFFFFF0;    //sp -> Stack polonger
    reg[3] = 0x10000000;    //data pointer
    RS1 = RS2 = RD = RM = RZ = RY = RA = RB = PC = IR = MuxB_select = MuxC_select = MuxINC_select = MuxY_select = MuxPC_select = MuxMA_select = RegFileAddrA = RegFileAddrB = RegFileAddrC = RegFileInp = RegFileAOut = RegFileBOut = MAR = MDR = opcode = numBytes = RF_Write = immed = PC_Temp = Mem_Write = Mem_Read = 0;
}

std::string ProcessorMemoryInterface() {
    if(MuxMA_select == 0) {
        if(Mem_Read==1) {
            std::vector<long long > t;
            for(long long  i = 0; i < numBytes; ++i) {
                t.push_back(dataMemory[MAR][i]);
            }
            reverse(t.begin(), t.end());
            std::string ans = "0x";
            for(auto i:t) {
                std::string curr = hex(i);
                for(long long  j = 0; j < 2-curr.size(); j++) ans+="0";
                ans+=curr;
            }
            return ans;
        }
        else if(Mem_Write==1) {
            
            for(long long  i = 0; i < numBytes; ++i) {
                
                std::string temp = "0xFF";
                for(long long  j = 0; j < 2*i; j++) temp+="0";
                long long  x = std::strtoull(temp.c_str(), nullptr, 16);
                if(dataMemory.find(MAR)!=dataMemory.end()) dataMemory[MAR][i] = (MDR & x)>>(8*i);
                else {
                    dataMemory[MAR].push_back((MDR & x)>>(8*i));
                }
                
            }
            return "0x1";
        }
    }
    else {
        std::vector<std::string> t = instructionMemory[MAR];
        std::string ans = "";
        long long  x = t.size();
        for(long long  i = 0; i < x; ++i) ans+=(t[x-1-i]);
        ans = "0x"+ans;
        return ans;
    }
    return "";
}

void GenerateControlSignals(long long  reg_write,long long  MuxB,long long  MuxY,long long  MemRead,long long  MemWrite,long long  MuxMA,long long  MuxPC,long long  MuxINC,long long  numB){
    RF_Write = reg_write;
    MuxB_select = MuxB;
    MuxY_select = MuxY;
    Mem_Write = MemWrite;
    Mem_Read = MemRead;
    MuxMA_select = MuxMA;
    MuxPC_select = MuxPC;
    MuxINC_select = MuxINC;
    numBytes = numB;
}

void fetch() {
    MAR = strtoull(("0x"+hex(PC)).c_str(), nullptr, 16);
    // std::cout<<hex(IR)<<"  "<<hex(PC)<<std::endl;
    MuxMA_select = 1;
    IR = strtoull(ProcessorMemoryInterface().c_str(), nullptr, 16);
    PC_Temp = PC+4;
}

void ImmediateSign(int num) {
    if((immed & ((1ULL << (num-1)))) == 0)
        return;
    immed ^= (1ULL << num) - 1;
    immed += 1;
    immed *= -1;
}

void Decode() {

    for(auto &i : ALUOp) i = 0; 

    long long  func3, func7;
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
                std::cout << "Invalid Func7 for Add/Sub/Mul";
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
                std::cout << "Invalid Func7 for And";
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
                std::cout << "Invalid Func7 for Or/Rem.";
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
                std::cout << "Invalid Func7 for SLL";
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
                std::cout << "Invalid Func7 for SLT";
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
                std::cout << "Invalid Instruction for SRA/SRL.";
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
                std::cout << "Invalid func7 fro XOR/DIV.";
                return;
            }
        }
        else{
            std::cout << "Func3 not matching in R format";
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
                std::cout << "Invalid func3 for lb/lw/lh.";
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
            else if(func3 == 0x6){
                // xori Instruction
                message = "This is xori Instruction.";
                ALUOp[5] = 1;
            }
            else if(func3 == 0x1){
                // slli Instruction
                message = "This is slli Instruction.";
                ALUOp[6] = 1;
            }
            else if(func3 == 0x5){
                // srli Instruction
                message = "This is srli Instruction.";
                ALUOp[8] = 1;
            }

            else{
                std::cout << "Invalid func3 for addi/andi/ori";
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
                std::cout << "Invalid func3 for jalr.";
                return;
            }

            RA = reg[RS1];      // Setting RA
            // RB and RM are DON"T CARES
        }
    }
    else if(opcode == 35){  // S Format

        RS1 = (IR & 0xF8000) >> 15;                 // Setting Source1 Register
        RS2 = (IR & 0x1F00000) >> 20;               // Setting Source2 Register
        long long  immed_4to0 = (IR & 0xF80) >> 7;         // Extracting immediate[4:0]
        long long  immed_11to5 = (IR & 0xFE000000) >> 25;  // Extracting immediate[11:5]
        immed = immed_4to0 | immed_11to5;           // Setting immediate
        ImmediateSign(12);  
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
            std::cout << "Invalid func3 for sb/sh/sw";
            return;
        }

        RA = reg[RS2];      // Setting RA
        RB = reg[RS1];      // Setting RB
        RM = RB;            // Setting RM
    }
    else if(opcode == 99) { // SB format
        RS1 = (IR & 0xF8000) >> 15;  // Setting Source1 Register
        RS2 = (IR & 0x1F00000) >> 20;  // Setting Source2 Register
        RA = reg[RS1];  // Setting RA
        RB = reg[RS2];  // Setting RB
        long long  imm1 = (IR & 0xF80) >> 7;
        long long  imm2 = (IR & 0x7E000000) >> 25;
        immed = 0;
        immed |= ((imm1 & 0x1E) >> 1);
        immed |= ((imm2 & 0x3F) << 4);
        immed |= ((imm1 & 0x1) << 10);
        immed |= (((imm2 & 0x40) >> 6) << 11);
        ImmediateSign(12);
        immed *= 2;
        // Setting control signals
        if(func3 == 0x0) {
            message = "This is BEQ instruction.";
            ALUOp[12] = 1;
        }
        else if(func3 == 0x1) {
            message = "This is BNE instruction.";
            ALUOp[13] = 1;
        }
        else if(func3 == 0x4) {
            message = "This is BLT instruction.";
            ALUOp[11] = 1;
        }
        else if(func3 == 0x5)
        {
            message = "This is BGE instruction.";
            ALUOp[14] = 1;
        }
        else {
            std::cout << "Invalid func3 for SB format.";
            return;
        }
        GenerateControlSignals(0,0,0,0,0,0,1,1,0);
    }
    else if(opcode == 23 || opcode == 55) { // U format
        RD = (IR & 0xF80) >> 7;
        immed = (IR & 0xFFFFF000) >> 12;
       
        ImmediateSign(20);
        if(opcode == 23) { // AUIPC
            message = "This is AUIPC instruction.";
            ALUOp[0] = 1;
            RA = PC;
            immed = immed << 12;
        }
        else { // LUI
            message = "This is LUI instruction.";
            ALUOp[6] = 1;
            RA = immed;
            immed = 12;
        }
         
        GenerateControlSignals(1,1,0,0,0,0,1,0,0);
    }
    else if(opcode == 111) { // UJ format
        message = "This is JALR instruction.";
        RD = (IR & 0xF80) >> 7;
        long long  immed_tmp = (IR & 0xFFFFF000) >> 12;
        immed = 0;
        immed |= (immed_tmp & 0x7FE00) >> 9;
        immed |= (immed_tmp & 0x100) << 2;
        immed |= (immed_tmp & 0xFF) << 11;
        immed |= (immed_tmp & 0x80000) >> 20;
        // ImmediateSign(20);
        immed *= 2;
        ALUOp[12] = 1;
        RA = 0;
        RB = 0;
        GenerateControlSignals(1,0,2,0,0,0,1,1,0);
    }
    else 
        std::cout << "Invalid opcode.";

}




// ---------------------------------------------FLOWCHART---------------------------------------------//
/*
                                                R TYPE
OPCODE          func3           func7       Instruction    ALUop(ON)
0110011          0x0            0x00            add         0
0110011          0x0            0x20            sub         1
0110011          0x0            0x01            mul         3
0110011          0x7            0x00            and         10
0110011          0x6            0x00            or          9
0110011          0x6            0x01            rem         4
0110011          0x1            0x00            sll         6
0110011          0x2            0x00            slt         11
0110011          0x5            0x00            srl         8
0110011          0x5            0x20            sra         7
0110011          0x4            0x00            xor         5
0110011          0x4            0x01            div         2
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




int Execute()
{
    long long  i=0;
    long long  InA, InB;
    InA = RA;
    if(MuxB_select==1)
    {
        InB=immed;
    }
    else InB = RB;
    
    for(auto &val :ALUOp)
    {
        if(val==1)
        {
            switch (i)
            {
                case 0:
                {
                    RZ=InA + InB;
                    break;
                }
                case 1:
                {
                    RZ=InA-InB;
                    break;
                }
                case 2:
                {
                    if(RB==0)//checking denominator!=0
                        return 1;
                    RZ = InA/InB;
                    break;
                }
                case 3:
                {
                    RZ=InA * InB;
                    break;
                }
                case 4:
                {
                    if(InB==0)
                        return 1;
                    RZ=InA % InB;
                    break;
                }
                case 5:
                {
                    RZ=InA ^ InB;
                    break;
                }
                case 6:
                {
                    if(InB < 0) 
                        return 1;
                    RZ=InA<<InB;
                    break;
                }
                case 7:
                {
                    
                    break;
                }
                case 8:
                {
                    if(InB<0) 
                        return 1;
                    RZ=InA>>InB;
                    break;
                }
                case 9:
                {
                    RZ=InA|InB;
                    break;
                }
                case 10:
                {
                    RZ=InA&InB;
                    break;
                }
                case 11:
                {
                    if(RA<RB)
                    {
                        RZ=1;
                    }
                    else
                    {
                        RZ=0;
                    }
                    MuxINC_select = RZ;
                    break;
                }
                case 12:
                {
                    RZ = (InA==InB);
                    MuxINC_select = RZ;
                    break;
                }  
                case 13:
                {
                    RZ = (InA!=InB);
                    MuxINC_select = RZ;
                    break;
                } 
                case 14:
                {
                    RZ = (InA>=InB);
                    MuxINC_select = RZ;
                    break;
                }
                default:
                {
                    break;
                }
            }
        }
        i++;
    }
    return 0;
}

// PC Update
void IAG() {
    if(MuxPC_select == 0)
        PC = RA;
    else {
        if(MuxINC_select == 0)
            PC += 4;
        else
            PC += immed;
    }
}

void MemoryAccess() {
    IAG();
    if(MuxY_select == 0){
        
        RY = RZ;
    }
    else if(MuxY_select == 1) {
        MAR = strtoull(("0x"+hex(RZ)).c_str(), nullptr, 16);
        MDR = RM;
        RY = strtoull((ProcessorMemoryInterface()).c_str(), nullptr, 16);
        
        if(RY > ((1ULL << 31) - 1))
            RY = -((1ULL << 32)-RY);
        
    }
    else if(MuxY_select == 2) 
        RY = PC_Temp;
}

void RegisterUpdate() {
    if(RF_Write == 1 && RD != 0)
        reg[RD] = RY;
}