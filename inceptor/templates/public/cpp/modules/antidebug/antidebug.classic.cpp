#include <Windows.h>
#include <winternl.h>
#include <psapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <TlHelp32.h>
#include <DbgHelp.h>
#include <thread>
#include <vector>
#include <iostream>

#define NT_FAIL(status) (status < 0)
#define FLG_HEAP_ENABLE_TAIL_CHECK 0x10
#define FLG_HEAP_ENABLE_FREE_CHECK 0x20
#define FLG_HEAP_VALIDATE_PARAMETERS 0x40
#define NT_GLOBAL_FLAG_DEBUGGED (FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS)
#define MAKEULONGLONG(ldw, hdw) ((ULONGLONG(hdw) << 32) | ((ldw) & 0xFFFFFFFF))

//####SHELLCODE####

typedef struct {
    LPVOID lpVirtualAddress;
    DWORD dwSizeOfRawData;
} SECTIONINFO, * PSECTIONINFO;

typedef struct {
    DWORD64 dwRealHash;
    SECTIONINFO SectionInfo;
} HASHSET, * PHASHSET;

typedef NTSTATUS(WINAPI* fnNtQueryInformationProcess) (
    HANDLE ProcessHandle,
    PROCESSINFOCLASS ProcessInformationCLass,
    PVOID ProcessInformation,
    ULONG ProcessInformationLength,
    PULONG ReturnLength
    );

typedef struct __PEB_LDR_DATA //, 7 elements, 0x28 bytes
{
    DWORD dwLength;
    DWORD dwInitialized;
    LPVOID lpSsHandle;
    LIST_ENTRY InLoadOrderModuleList;
    LIST_ENTRY InMemoryOrderModuleList;
    LIST_ENTRY InInitializationOrderModuleList;
    LPVOID lpEntryInProgress;
} __PEB_LDR_DATA, * __PPEB_LDR_DATA;

// WinDbg> dt -v ntdll!_PEB_FREE_BLOCK
typedef struct _PEB_FREE_BLOCK // 2 elements, 0x8 bytes
{
    struct _PEB_FREE_BLOCK* pNext;
    DWORD dwSize;
} PEB_FREE_BLOCK, * PPEB_FREE_BLOCK;

typedef struct __PEB // 65 elements, 0x210 bytes
{
    BYTE bInheritedAddressSpace;
    BYTE bReadImageFileExecOptions;
    BYTE bBeingDebugged;
    BYTE bSpareBool;
    LPVOID lpMutant;
    LPVOID lpImageBaseAddress;
    __PPEB_LDR_DATA pLdr;
    LPVOID lpProcessParameters;
    LPVOID lpSubSystemData;
    LPVOID lpProcessHeap;
    PRTL_CRITICAL_SECTION pFastPebLock;
    LPVOID lpFastPebLockRoutine;
    LPVOID lpFastPebUnlockRoutine;
    DWORD dwEnvironmentUpdateCount;
    LPVOID lpKernelCallbackTable;
    DWORD dwSystemReserved;
    DWORD dwAtlThunkSListPtr32;
    LPVOID lpApiSetMap;				// used to be PPEB_FREE_BLOCK pFreeList;
    DWORD dwTlsExpansionCounter;
    LPVOID lpTlsBitmap;
    DWORD dwTlsBitmapBits[2];
    LPVOID lpReadOnlySharedMemoryBase;
    LPVOID lpReadOnlySharedMemoryHeap;
    LPVOID lpReadOnlyStaticServerData;
    LPVOID lpAnsiCodePageData;
    LPVOID lpOemCodePageData;
    LPVOID lpUnicodeCaseTableData;
    DWORD dwNumberOfProcessors;
    DWORD dwNtGlobalFlag;
    LARGE_INTEGER liCriticalSectionTimeout;
    DWORD dwHeapSegmentReserve;
    DWORD dwHeapSegmentCommit;
    DWORD dwHeapDeCommitTotalFreeThreshold;
    DWORD dwHeapDeCommitFreeBlockThreshold;
    DWORD dwNumberOfHeaps;
    DWORD dwMaximumNumberOfHeaps;
    LPVOID lpProcessHeaps;
    LPVOID lpGdiSharedHandleTable;
    LPVOID lpProcessStarterHelper;
    DWORD dwGdiDCAttributeList;
    LPVOID lpLoaderLock;
    DWORD dwOSMajorVersion;
    DWORD dwOSMinorVersion;
    WORD wOSBuildNumber;
    WORD wOSCSDVersion;
    DWORD dwOSPlatformId;
    DWORD dwImageSubsystem;
    DWORD dwImageSubsystemMajorVersion;
    DWORD dwImageSubsystemMinorVersion;
    DWORD dwImageProcessAffinityMask;
    DWORD dwGdiHandleBuffer[34];
    LPVOID lpPostProcessInitRoutine;
    LPVOID lpTlsExpansionBitmap;
    DWORD dwTlsExpansionBitmapBits[32];
    DWORD dwSessionId;
    ULARGE_INTEGER liAppCompatFlags;
    ULARGE_INTEGER liAppCompatFlagsUser;
    LPVOID lppShimData;
    LPVOID lpAppCompatInfo;
    UNICODE_STRING usCSDVersion;
    LPVOID lpActivationContextData;
    LPVOID lpProcessAssemblyStorageMap;
    LPVOID lpSystemDefaultActivationContextData;
    LPVOID lpSystemAssemblyStorageMap;
    DWORD dwMinimumStackCommit;
} __PEB, * __PPEB;

__PPEB GetProcessEnvironmentBlock()
{
    ULONG_PTR pPeb;
#ifdef _WIN64
    pPeb = __readgsqword(0x60);
#else
    // _WIN32
    pPeb = __readfsdword(0x30);
#endif
    return (__PPEB)pPeb;
}

fnNtQueryInformationProcess GetNtQueryInformationProcess() {
    HMODULE hNtdll = GetModuleHandleW(L"ntdll.dll");
    if (hNtdll == NULL) {
        return NULL;
    }

    FARPROC func = GetProcAddress(hNtdll, "NtQueryInformationProcess");
    fnNtQueryInformationProcess query_func = (fnNtQueryInformationProcess)func;

    return query_func;
}

DWORD GetPidByProcessName(WCHAR* name) {
    PROCESSENTRY32W entry;
    memset(&entry, 0, sizeof(PROCESSENTRY32W));
    entry.dwSize = sizeof(PROCESSENTRY32W);

    DWORD pid = -1;
    HANDLE hSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
    if (Process32FirstW(hSnapShot, &entry)) {
        do {
            if (!wcscmp(name, entry.szExeFile)) {
                pid = entry.th32ProcessID;
                break;
            }
        } while (Process32Next(hSnapShot, &entry));
    }

    CloseHandle(hSnapShot);

    return pid;
}

DWORD GetMainThreadId(DWORD pid) {
    THREADENTRY32 th32;
    memset(&th32, 0, sizeof(THREADENTRY32));
    th32.dwSize = sizeof(THREADENTRY32);

    DWORD dwMainThreadID = -1;

    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, NULL);
    if (Thread32First(hSnapshot, &th32)) {
        DWORD64 ullMinCreateTime = 0xFFFFFFFFFFFFFFFF;

        do {
            if (th32.th32OwnerProcessID == pid) {
                HANDLE hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, th32.th32ThreadID);

                if (hThread) {
                    FILETIME afTimes[4] = { 0 };
                    if (GetThreadTimes(hThread, &afTimes[0], &afTimes[1], &afTimes[2], &afTimes[3])) {
                        ULONGLONG ullTest = MAKEULONGLONG(afTimes[0].dwLowDateTime, afTimes[0].dwHighDateTime);
                        if (ullTest && ullTest < ullMinCreateTime) {
                            ullMinCreateTime = ullTest;
                            dwMainThreadID = th32.th32ThreadID;
                        }
                    }
                    CloseHandle(hThread);
                }
            }
        } while (Thread32Next(hSnapshot, &th32));
    }

    CloseHandle(hSnapshot);
    return dwMainThreadID;
}

int GetAllModule(std::vector<LPVOID>& modules) {
    MODULEENTRY32W mEntry;
    memset(&mEntry, 0, sizeof(mEntry));
    mEntry.dwSize = sizeof(MODULEENTRY32);

    DWORD curPid = GetCurrentProcessId();

    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, NULL);
    if (Module32FirstW(hSnapshot, &mEntry)) {
        do {
            modules.emplace_back(mEntry.modBaseAddr);
        } while (Module32NextW(hSnapshot, &mEntry));
    }

    CloseHandle(hSnapshot);

    if (modules.empty()) {
        return -1;
    }

    return 0;
}

int GetTextSectionInfo(LPVOID lpModBaseAddr, PSECTIONINFO info) {
    PIMAGE_NT_HEADERS pNtHdr = ImageNtHeader(lpModBaseAddr);
    PIMAGE_SECTION_HEADER pSectionHeader = (PIMAGE_SECTION_HEADER)(pNtHdr + 1);

    LPVOID lpTextAddr = NULL;
    DWORD dwSizeOfRawData = NULL;

    for (int i = 0; i < pNtHdr->FileHeader.NumberOfSections; ++i) {
        char* name = (char*)pSectionHeader->Name;

        if (!strcmp(name, ".text")) {
            info->lpVirtualAddress = (LPVOID)((DWORD64)lpModBaseAddr + pSectionHeader->VirtualAddress);
            info->dwSizeOfRawData = pSectionHeader->SizeOfRawData;
            break;
        }

        ++pSectionHeader;
    }

    if (info->dwSizeOfRawData == NULL) {
        return -1;
    }

    return 0;
}

DWORD64 HashSection(LPVOID lpSectionAddress, DWORD dwSizeOfRawData) {
    DWORD64 hash = 0;
    BYTE* str = (BYTE*)lpSectionAddress;
    for (unsigned int i = 0; i < dwSizeOfRawData; ++i, ++str) {
        if (*str) {
            hash = *str + (hash << 6) + (hash << 16) - hash;
        }
    }

    return hash;
}

bool bTerminateThread = false;

bool CheckTextHash(PHASHSET pHashSet) {
    DWORD64 dwRealHash = pHashSet->dwRealHash;
    DWORD dwSizeOfRawData = pHashSet->SectionInfo.dwSizeOfRawData;
    LPVOID lpVirtualAddress = pHashSet->SectionInfo.lpVirtualAddress;

    while (1) {
        Sleep(1000);

        DWORD64 dwCurrentHash = HashSection(lpVirtualAddress, dwSizeOfRawData);
        if (dwRealHash != dwCurrentHash) {
            return true;
        }

        if (bTerminateThread) {
            return false;
        }
    }
}

int ExitThreads(std::vector<std::thread>& threads) {
    bTerminateThread = true;

    for (auto& thread : threads) {
        thread.join();
    }

    return 0;
}

int check_text_hash() {
    std::vector<LPVOID> modules;
    GetAllModule(modules);

    std::vector<std::thread> threads;
    threads.reserve(modules.size());

    std::vector<HASHSET> hashes;
    hashes.reserve(modules.size());

    for (auto& module : modules) {
        SECTIONINFO info;
        GetTextSectionInfo(module, &info);

        DWORD64 dwRealHash = HashSection(info.lpVirtualAddress, info.dwSizeOfRawData);
        hashes.emplace_back(HASHSET{ dwRealHash, info });
        threads.emplace_back(std::thread(CheckTextHash, &hashes.back()));
    }
    ExitThreads(threads);

    return 0;
}

bool veh_check(DWORD pid) {
    fnNtQueryInformationProcess NtQueryInformationProcess = GetNtQueryInformationProcess();

    ULONG ReturnLength;
    PROCESS_BASIC_INFORMATION pbi;
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);

    NtQueryInformationProcess(hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), &ReturnLength);
    PPEB pPEB = (PPEB)pbi.PebBaseAddress;

    SIZE_T Written;
    DWORD64 CrossProcessFlags = -1;
    ReadProcessMemory(hProcess, (PBYTE)pPEB + 0x50, (LPVOID)&CrossProcessFlags, sizeof(DWORD64), &Written);

    if (CrossProcessFlags & 0x4) {
        return true;
    }
    else {
        return false;
    }
}

void dr_register_check(DWORD pid) {

    DWORD tid = GetMainThreadId(pid);

    HANDLE hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, tid);
    if (hThread == NULL) {
        return;
    }

    CONTEXT ctx;
    memset(&ctx, 0, sizeof(CONTEXT));
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;

    ctx.Dr0 = 0;
    ctx.Dr1 = 0;
    ctx.Dr2 = 0;
    ctx.Dr3 = 0;
    ctx.Dr7 &= (0xffffffffffffffff ^ (0x1 | 0x4 | 0x10 | 0x40));

    SetThreadContext(hThread, &ctx);
    CloseHandle(hThread);
}

bool check_debug_string(void) {
    DWORD errorValue = 1111;
    SetLastError(errorValue);
    OutputDebugString(L" ");
    return (GetLastError() != errorValue);
}

bool is_being_debugged() {
    __PPEB peb = GetProcessEnvironmentBlock();
    if (peb->bBeingDebugged) {
        return true;
    }
    if (peb->dwNtGlobalFlag & NT_GLOBAL_FLAG_DEBUGGED) {
        return true;
    }
    return false;
}

bool ####FUNCTION####(){
    return (is_being_debugged() || check_debug_string() || veh_check(GetCurrentProcessId()));
}