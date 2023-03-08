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

std::string ProcessMemInterface() {
    if(MuxMA_select == 0) {
        if(Mem_Read==1) {
            std::vector<int> t;
            for(int i = 0; i < numBytes; ++i) {
                t.push_back(dataMemory[MAR][i]);
            }
            reverse(t.begin(), t.end());
            std::string ans = "0x";
            for(auto i:t) {
                std::string curr = hex(i);
                for(int j = 0; j < 2-curr.size(); j++) ans+="0";
                ans+=curr;
            }
            return ans;
        }
        else if(Mem_Write==1) {
            for(int i = 0; i < numBytes; ++i) {
                std::string temp = "0xFF";
                for(int j = 0; j < 2*i; j++) temp+="0";
                int x = std::strtol(temp.c_str(), nullptr, 16);
                dataMemory[MAR][i] = (MDR & x)>>(8*i);
            }
            return "0x1";
        }
    }
    else {
        std::vector<int> t = instructionMemory[MAR];
        std::string ans = "";
        int x = t.size();
        for(int i = 0; i < x; ++i) ans+=(t[x-1-i]+'0');
        ans = "0x"+ans;
        return ans;
    }
}

// Utility function to convert long integer to hexadecimal string
std::string hex(long n) {
    std::string ans = "";
    while (n != 0) {
        int rem = 0;
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