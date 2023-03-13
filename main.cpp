#include<iostream>
#include<map>
#include<vector>
#include<string>
#include"utility.hpp"
#include<fstream>

using namespace std;

long long reg[32] = {0};
long long RS1,RS2,RD,RM,RZ,RY,RA,RB,PC,IR,MuxB_select,MuxC_select,MuxINC_select,MuxY_select,MuxPC_select,MuxMA_select,RegFileAddrA,RegFileAddrB,RegFileAddrC,RegFileInp,RegFileAOut,RegFileBOut,MAR,MDR,opcode,numBytes,RF_Write,immed,PC_Temp,Mem_Write,Mem_Read;
long long ALUOp[15] = {0};
long long ui, clk;
long long stepClick = 0;
std::map<long long  , std::vector<long long  >> dataMemory;
std::map<long long  , std::vector<std::string>> instructionMemory;

bool validateDataSegment(vector<string> a);
bool validateInstruction(vector<string> a);

int main() {
    ifstream mcFile("input.mc");
    ofstream out("output.txt");
    bool flag = 0;
    string y;
    while(getline(mcFile, y)) {
        vector<string> x;
        string temp = "";
        for(auto it:y) {
            if(it==' ' || it=='\t') {
                if(temp.size()>1 || (temp!=" " && temp!="\t")) x.push_back(temp);
                temp = "";
                continue;
            }
            temp+=it;
        }
        if(temp.size()>0) x.push_back(temp);
        if(flag==1) {
            if(validateDataSegment(x)==0) {
                cout<<"Invalid Data segment"<<x[0]<<"\n";
                mcFile.close();
                return 1;
            }
            long long x1 = strtoull(x[0].c_str(), nullptr, 16);
            dataMemory[x1].push_back((strtoull(x[1].c_str(), nullptr, 16)) & strtoull("0xFF", nullptr, 16));
            dataMemory[x1].push_back(((strtoull(x[1].c_str(), nullptr, 16)) & strtoull("0xFF00", nullptr, 16))>>8);
            dataMemory[x1].push_back(((strtoull(x[1].c_str(), nullptr, 16)) & strtoull("0xFF0000", nullptr, 16))>>16);
            dataMemory[x1].push_back(((strtoull(x[1].c_str(), nullptr, 16)) & strtoull("0xFF000000", nullptr, 16))>>24);
        }
        for(auto it:x) if(it=="$") flag = 1;
        if(flag == 0) {
            if(validateInstruction(x)==0) {
                cout<<"Invalid Instruction segment"<<x[1]<<"\n";
                mcFile.close();
                return 1;
            }
            long long x1 = strtoull(x[0].c_str(), nullptr, 16);
            for(int i = 0; i < 4; ++i) {
                string temps = "0xFF";
                for(int j = 0; j < 2*i; ++j) temps+="0";
                instructionMemory[x1].push_back(hex((strtoull(x[1].c_str(), nullptr, 16) & strtoull(temps.c_str(), nullptr, 16)) >> (8*i)));
                temps = "";
                if((2-instructionMemory[x1][i].size()) > 0) for(int j = 0; j < (2-instructionMemory[x1][i].size()); ++j) temps+="0";
                instructionMemory[x1][i] = temps + instructionMemory[x1][i];
            }
        }
    }
    out<<"INSTRUCTIONS :\n";
    for(auto it:instructionMemory) {out<<hex(it.first)<<" "; for(auto j:it.second) out<<j<<" "; out<<"\n";}
    out<<"DATA :\n";
    for(auto it:dataMemory) {out<<hex(it.first)<<" "; for(auto j:it.second) out<<j<<" "; out<<"\n";}
    mcFile.close();
    out.close();
    
    return 0;
}

bool validateDataSegment(vector<string> a) {
    if(a.size() != 2) return 0;
    string addr = a[0];
    string data = a[1];
    if((addr[0]!='0'&& addr[1]!='x') || (data[0]!='0' && data[1]!='x')) return 0;
    try
    {
        if(strtoull(addr.c_str(), nullptr, 16) < strtoull("0x10000000", nullptr, 16)) return 0;
        strtoull(data.c_str(), nullptr, 16);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
    return 1;
}

bool validateInstruction(vector<string> a) {
    if(a.size() != 2) return 0;
    string addr = a[0];
    string data = a[1];
    try
    {
        strtoull(addr.c_str(), nullptr, 16);
        strtoull(data.c_str(), nullptr, 16);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
    return 1;
}
