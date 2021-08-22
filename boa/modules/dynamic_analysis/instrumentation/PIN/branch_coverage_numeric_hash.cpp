/*
 * Original script downloaded from: https://github.com/mothran/aflpin/blob/master/aflpin.cpp
 *
 * Modified in order to work with BOA.
 */

#include <pin.H>
#include <string>
#include <cstdlib>
#include <unistd.h>
#include <iostream>
#include <sys/shm.h>
#include <sys/wait.h>
#include <fstream>
#include <vector>
#include <stdint.h>
#include <numeric>

// Functions
uint32_t MurmurHash2(const void*, int, uint32_t);

// 65536
#define MAP_SIZE    (1 << 16)
#define FORKSRV_FD  198

//  CLI options -----------------------------------------------------------

KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "branchcount.out", "specify output file name");
KNOB<BOOL> Knob_debug(KNOB_MODE_WRITEONCE,  "pintool", "debug", "0", "Enable debug mode");

//  Global Vars -----------------------------------------------------------

std::ofstream OutFile;
ADDRINT sec_addr = 0;
UINT64  sec_size = 0;
ADDRINT min_addr = 0;
ADDRINT max_addr = 0;

std::vector<ADDRINT> branch_sources;
std::vector<ADDRINT> branch_jumps;
std::vector<std::string> branch_jumps_instr;

unsigned char bitmap[MAP_SIZE];
uint8_t *bitmap_shm = 0;

ADDRINT last_id = 0;

//  inlined functions -----------------------------------------------------

inline ADDRINT valid_addr(ADDRINT addr)
{
    if ( addr >= min_addr && addr <= max_addr )
        return true;

    return false;
}

//  Inserted functions ----------------------------------------------------


// Unused currently but could become a fast call in the future once I have tested it more.
VOID TrackBranch(ADDRINT cur_addr)
{
    ADDRINT cur_id = cur_addr - min_addr;

    // if (Knob_debug) {
    //     std::cout << "\nCURADDR:  0x" << cur_addr << std::endl;
    //     std::cout << "rel_addr: 0x" << (cur_addr - min_addr) << std::endl;
    //     std::cout << "cur_id:  " << cur_id << std::endl;
    //     std::cout << "index:  " << ((cur_id ^ last_id) % MAP_SIZE) << std::endl;
    // }

    if (bitmap_shm != 0){
        bitmap_shm[((cur_id ^ last_id) % MAP_SIZE)]++;
    }
    else {
        bitmap[((cur_id ^ last_id) % MAP_SIZE)]++;
    }
    last_id = cur_id;
}

//  Analysis functions ----------------------------------------------------

VOID Trace(TRACE trace, VOID *v)
{
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
        for (INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins = INS_Next(ins))
        {
            // make sure it is in a segment we want to instrument!
            if (valid_addr(INS_Address(ins)))
            {
                if (INS_IsBranch(ins)) {
                    // As per afl-as.c we only care about conditional branches (so no JMP instructions)
                    if (INS_HasFallThrough(ins) || INS_IsCall(ins))
                    {
                        ADDRINT branch_source = INS_Address(ins);
                        std::string branch_ins_disassemble = INS_Disassemble(ins);
                        std::string branch_jump_instr;
                        ADDRINT branch_jump;
                        std::stringstream ss;

                        size_t start = 0U;
                        size_t end = branch_ins_disassemble.find(" ");

                        while (end != std::string::npos)
                        {
                            branch_jump_instr = branch_ins_disassemble.substr(start, end - start);
                            start = end + 1;
                            end = branch_ins_disassemble.find(" ", start);
                        }

                        ss << std::hex << branch_ins_disassemble.substr(start, end - start);
                        ss >> branch_jump;

                        if (Knob_debug)
                        {
                            //std::cerr << "BRANCH: 0x" << std::hex << branch_source << ":\t" << branch_ins_disassemble << std::endl;
                            std::cerr << "BRANCH: 0x" << std::hex << branch_source << ":\t" << branch_jump_instr << " 0x" << branch_jump << std::endl;
                        }

                        // Store results
                        branch_sources.push_back(sec_addr - branch_source);
                        branch_jumps_instr.push_back(branch_jump_instr);
                        branch_jumps.push_back(sec_addr - branch_jump);

                        // Instrument the code.
                        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)TrackBranch,
                            IARG_INST_PTR,
                            IARG_END);
                    }
                }
            }
        }
    }
}

VOID entry_point(VOID *ptr)
{
    /*  Much like the original instrumentation from AFL we only want to instrument the segments of code
     *  from the actual application and not the link and PIN setup itself.
     *
     *  Inspired by: http://joxeankoret.com/blog/2012/11/04/a-simple-pin-tool-unpacker-for-the-linux-version-of-skype/
     */

    IMG img = APP_ImgHead();
    for(SEC sec= IMG_SecHead(img); SEC_Valid(sec); sec = SEC_Next(sec))
    {
        // lets sanity check the exec flag 
        // TODO: the check for .text name might be too much, there could be other executable segments we
        //       need to instrument but maybe not things like the .plt or .fini/init
        // IF this changes, we need to change the code in the instrumentation code, save all the base addresses.

        if (SEC_IsExecutable(sec) && SEC_Name(sec) == ".text")
        {
            sec_addr = SEC_Address(sec);
            sec_size = SEC_Size(sec);
            
            if (Knob_debug)
            {
                std::cerr << "Name: " << SEC_Name(sec) << std::endl;
                std::cerr << "Addr: 0x" << std::hex << sec_addr << std::endl;
                std::cerr << "Size: " << sec_size << std::endl << std::endl;
            }

            if (sec_addr != 0)
            {
                ADDRINT high_addr = sec_addr + sec_size;

                if (sec_addr > min_addr || min_addr == 0)
                    min_addr = sec_addr;

                // Now check and set the max_addr.
                if (sec_addr > max_addr || max_addr == 0)
                    max_addr = sec_addr;

                if (high_addr > max_addr)
                    max_addr = high_addr;
            }
        }
    }
    if (Knob_debug)
    {
        std::cerr << "min_addr:\t0x" << std::hex << min_addr << std::endl;
        std::cerr << "max_addr:\t0x" << std::hex << max_addr << std::endl << std::endl;
    }
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID* v)
{
    // Write to a file since cout and cerr maybe closed by the application
    OutFile.setf(std::ios::showbase);

    uint32_t seed = 0x726f7373;
    uint32_t branch_sources_hash = MurmurHash2(&branch_sources[0], branch_sources.size() * sizeof(ADDRINT), seed);
    std::string branch_jumps_instr_concatenation = std::accumulate(branch_jumps_instr.begin(), branch_jumps_instr.end(), std::string(""));
    uint32_t branch_jumps_instr_hash = MurmurHash2(&branch_jumps_instr_concatenation[0], branch_jumps_instr_concatenation.size(), seed);
    uint32_t branch_jumps_hash = MurmurHash2(&branch_jumps[0], branch_jumps.size() * sizeof(ADDRINT), seed);
    std::vector<uint32_t> final_hash_aux;

    final_hash_aux.push_back(branch_sources_hash);
    final_hash_aux.push_back(branch_jumps_instr_hash);
    final_hash_aux.push_back(branch_jumps_hash);

    uint32_t final_hash = MurmurHash2(&final_hash_aux[0], final_hash_aux.size() * sizeof(uint32_t), seed);

    // WARNING: final_hash is a representation of the executed branch, not a reward value!
    // Format: reward<tab>id
    OutFile << branch_sources.size() << "\t" << final_hash << std::endl;

    OutFile.close();
}

// Main functions ------------------------------------------------

INT32 Usage()
{
    std::cerr << "AFLPIN -- A pin tool to enable blackbox binaries to be fuzzed with AFL on Linux" << std::endl;
    std::cerr << "   -o     --  output file.";
    std::cerr << "   -debug --  prints extra debug information." << std::endl;
    return -1;
}

int main(int argc, char *argv[])
{
    if(PIN_Init(argc, argv))
    {
        return Usage();
    }

    OutFile.open(KnobOutputFile.Value().c_str());

    PIN_SetSyntaxIntel();
    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddApplicationStartFunction(entry_point, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();
}

// MurmurHash2 (code obtained from https://github.com/aappleby/smhasher/blob/master/src/MurmurHash2.{h,cpp})

uint32_t MurmurHash2(const void* key, int len, uint32_t seed)
{
  // 'm' and 'r' are mixing constants generated offline.
  // They're not really 'magic', they just happen to work well.

  const uint32_t m = 0x5bd1e995;
  const int r = 24;

  // Initialize the hash to a 'random' value

  uint32_t h = seed ^ len;

  // Mix 4 bytes at a time into the hash

  const unsigned char* data = (const unsigned char*)key;

  while(len >= 4)
  {
    uint32_t k = *(uint32_t*)data;

    k *= m;
    k ^= k >> r;
    k *= m;

    h *= m;
    h ^= k;

    data += 4;
    len -= 4;
  }

  // Handle the last few bytes of the input array

  switch(len)
  {
  case 3: h ^= data[2] << 16;
  case 2: h ^= data[1] << 8;
  case 1: h ^= data[0];
      h *= m;
  };

  // Do a few final mixes of the hash to ensure the last few
  // bytes are well-incorporated.

  h ^= h >> 13;
  h *= m;
  h ^= h >> 15;

  return h;
} 
