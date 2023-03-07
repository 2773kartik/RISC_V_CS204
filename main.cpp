#include<iostream>
#include<map>
#include<vector>
#include<string>
#include"utility.hpp"

using namespace std;

long reg[32] = {0};
long RS1,RS2,RD,RM,RZ,RY,RA,RB,PC,IR,MuxB_select,MuxC_select,MuxINC_select,MuxY_select,MuxPC_select,MuxMA_select,RegFileAddrA,RegFileAddrB,RegFileAddrC,RegFileInp,RegFileAOut,RegFileBOut,MAR,MDR,opcode,numBytes,RF_Write,immed,PC_Temp,Mem_Write,Mem_Read;
long ALU[15] = {0};
long ui, clk;
long stepClick = 0;
std::map<int, std::vector<int>> dataMemory;
std::map<int, std::vector<int>> instructionMemory;

int main() {
    cout<<reg[2]<<"\n";
    init();
    cout<<reg[2]<<"\n";
}