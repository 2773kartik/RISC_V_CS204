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
    for(auto i : ALU) i = 0;
    for(auto i : reg) i = 0;
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