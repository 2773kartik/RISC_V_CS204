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
long long isStepClicked = 0;
std::map<long long  , std::vector<long long  >> dataMemory;
std::map<long long  , std::vector<std::string>> instructionMemory;

bool validateDataSegment(vector<string> a);
bool validateInstruction(vector<string> a);
void run_RISC_simulator();

int main() {
    ifstream mcFile("input.mc");
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
            long long x1 = strtoll(x[0].c_str(), nullptr, 16);
            dataMemory[x1].push_back((strtoll(x[1].c_str(), nullptr, 16)) & strtoll("0xFF", nullptr, 16));
            dataMemory[x1].push_back(((strtoll(x[1].c_str(), nullptr, 16)) & strtoll("0xFF00", nullptr, 16))>>8);
            dataMemory[x1].push_back(((strtoll(x[1].c_str(), nullptr, 16)) & strtoll("0xFF0000", nullptr, 16))>>16);
            dataMemory[x1].push_back(((strtoll(x[1].c_str(), nullptr, 16)) & strtoll("0xFF000000", nullptr, 16))>>24);
        }
        for(auto it:x) if(it=="$") flag = 1;
        if(flag == 0) {
            if(validateInstruction(x)==0) {
                cout<<"Invalid Instruction segment"<<x[1]<<"\n";
                mcFile.close();
                return 1;
            }
            long long x1 = strtoll(x[0].c_str(), nullptr, 16);
            for(int i = 0; i < 4; ++i) {
                string temps = "0xFF";
                for(int j = 0; j < 2*i; ++j) temps+="0";
                instructionMemory[x1].push_back(hex((strtoll(x[1].c_str(), nullptr, 16) & strtoll(temps.c_str(), nullptr, 16)) >> (8*i)));
                temps = "";
                if((2-instructionMemory[x1][i].size()) > 0) for(int j = 0; j < (2-instructionMemory[x1][i].size()); ++j) temps+="0";
                instructionMemory[x1][i] = temps + instructionMemory[x1][i];
            }
        }
    }
    mcFile.close();
    
    run_RISC_simulator();
    return 0;
}

bool validateDataSegment(vector<string> a) {
    if(a.size() != 2) return 0;
    string addr = a[0];
    string data = a[1];
    if((addr[0]!='0'&& addr[1]!='x') || (data[0]!='0' && data[1]!='x')) return 0;
    try
    {
        if(strtoll(addr.c_str(), nullptr, 16) < strtoll("0x10000000", nullptr, 16)) return 0;
        strtoll(data.c_str(), nullptr, 16);
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
        strtoll(addr.c_str(), nullptr, 16);
        strtoll(data.c_str(), nullptr, 16);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
    return 1;
}

void run_RISC_simulator() {
    init();
    bool flag = 1;
    ofstream out("output.txt");
    ofstream json("out.json");
    long long i = 0;
    json<<"{\n";
    while((instructionMemory.find(strtoll(("0x"+hex(PC)).c_str(), nullptr, 16)) != instructionMemory.end()) && flag) {
        json<<"\t\""<<i<<"\": {\n";
        fetch();
        string msg = Decode();
        Execute();
        MemoryAccess();
        RegisterUpdate();
        clk += 1;
        if(isStepClicked==1) {
            isStepClicked=0;
            flag=0;
        }
        json<<"\t\t\"PC\":"<<PC<<",\n";
        json<<"\t\t\"Reg\": ["; for(auto &val:reg) json<<val<<", "; json<<reg[31]<<"],\n";
        json<<"\t\t\"Message\": \""<<msg<<"\",\n";
        json<<"\t\t\"Data\": {\n";
        for(auto it:dataMemory) {
            json<<"\t\t\t\"0x"<<hex(it.first)<<"\": ["; 
            for(auto j:it.second) json<<j<<" , ";
            json.seekp(-3, std::ios_base::end);
            json<<"],\n";
        }
        json.seekp(-3, std::ios_base::end); json<<"\n";
        json<<"\t\t}\n";
        json<<"\t},\n";
        ++i;
    }
    json.seekp(-3, std::ios_base::end); json<<"\n";
    json<<"}";
    json.close();
    out<<"REGISTERS :\n";
    for(auto it:reg) out<<it<<"\n";
    out<<"DATA :\n";
    for(auto it:dataMemory) {out<<hex(it.first)<<" "; for(auto j:it.second) out<<j<<" "; out<<"\n";}
    out.close();
    return;
}