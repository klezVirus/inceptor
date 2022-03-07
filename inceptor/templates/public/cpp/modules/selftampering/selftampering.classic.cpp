#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <psapi.h>

#define DEBUG 0

HMODULE GetMainModule(HANDLE);
BOOL GetMainModuleInformation(PULONG64, PULONG64);
void ####FUNCTION####(unsigned char[], unsigned char[]);

HMODULE GetMainModule(HANDLE hProcess)
{
	HMODULE mainModule = NULL;
	HMODULE* lphModule;
	LPBYTE lphModuleBytes;
	DWORD lpcbNeeded;

	// First call needed to know the space (bytes) required to store the modules' handles
	BOOL success = EnumProcessModules(hProcess, NULL, 0, &lpcbNeeded);

	// We already know that lpcbNeeded is always > 0
	if (!success || lpcbNeeded == 0)
	{
		printf("[-] Error enumerating process modules\n");
		// At this point, we already know we won't be able to dyncamically
		// place the syscall instruction, so we can exit
		exit(1);
	}
	// Once we got the number of bytes required to store all the handles for
	// the process' modules, we can allocate space for them
	lphModuleBytes = (LPBYTE)LocalAlloc(LPTR, lpcbNeeded);

	if (lphModuleBytes == NULL)
	{
		printf("[-] Error allocating memory to store process modules handles\n");
		exit(1);
	}
	unsigned int moduleCount;

	moduleCount = lpcbNeeded / sizeof(HMODULE);
	lphModule = (HMODULE*)lphModuleBytes;

	success = EnumProcessModules(hProcess, lphModule, lpcbNeeded, &lpcbNeeded);

	if (!success)
	{
		printf("[-] Error enumerating process modules\n");
		exit(1);
	}

	// Finally storing the main module
	mainModule = lphModule[0];

	// Avoid memory leak
	LocalFree(lphModuleBytes);

	// Return main module
	return mainModule;
}

BOOL GetMainModuleInformation(PULONG64 startAddress, PULONG64 length)
{
	HANDLE hProcess = GetCurrentProcess();
	HMODULE hModule = GetMainModule(hProcess);
	MODULEINFO mi;

	GetModuleInformation(hProcess, hModule, &mi, sizeof(mi));

	printf("Base Address: 0x%llu\n", (ULONG64)mi.lpBaseOfDll);
	printf("Image Size:   %u\n", (ULONG)mi.SizeOfImage);
	printf("Entry Point:  0x%llu\n", (ULONG64)mi.EntryPoint);
	printf("\n");

	*startAddress = (ULONG64)mi.lpBaseOfDll;
	*length = (ULONG64)mi.SizeOfImage;

	DWORD oldProtect;
	VirtualProtect(mi.lpBaseOfDll, mi.SizeOfImage, PAGE_EXECUTE_READWRITE, &oldProtect);

	return 0;
}

void ####FUNCTION####(unsigned char egg[], unsigned char replace[])
{

	ULONG64 startAddress = 0;
	ULONG64 size = 0;

	GetMainModuleInformation(&startAddress, &size);

	if (size <= 0) {
		printf("[-] Error detecting main module size");
		exit(1);
	}

	ULONG64 currentOffset = 0;

	unsigned char* current = (unsigned char*)malloc(8*sizeof(unsigned char*));
	SIZE_T nBytesRead;

	printf("Starting search from: 0x%llu\n", (ULONG64)startAddress + currentOffset);

	while (currentOffset < size - 8)
	{
		currentOffset++;
		LPVOID currentAddress = (LPVOID)(startAddress + currentOffset);
		if(DEBUG > 0){
    		printf("Searching at 0x%llu\n", (ULONG64)currentAddress);
        }
		if (!ReadProcessMemory((HANDLE)((int)-1), currentAddress, current, 8, &nBytesRead)) {
			printf("[-] Error reading from memory\n");
			exit(1);
		}
		if (nBytesRead != 8) {
			printf("[-] Error reading from memory\n");
			continue;
		}

        if(DEBUG > 0){
            for (int i = 0; i < nBytesRead; i++){
                printf("%02x ", current[i]);
            }
            printf("\n");
        }

		if (memcmp(egg, current, 8) == 0)
		{
			printf("Found at %llu\n", (ULONG64)currentAddress);
			WriteProcessMemory((HANDLE)((int)-1), currentAddress, replace, 8, &nBytesRead);
		}

	}
	printf("Ended search at:   0x%llu\n", (ULONG64)startAddress + currentOffset);
	free(current);
}