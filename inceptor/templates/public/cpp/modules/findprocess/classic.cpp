#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <Tlhelp32.h>
#include <string.h>

#define ARRAY_COUNT(array) (sizeof(array)/sizeof(array[0]))

DWORD find_process_single(const wchar_t*);
DWORD ####FUNCTION####();

DWORD ####FUNCTION####(){
    const wchar_t* processes[] =
    {
        ####PROCESS####
    };

    DWORD pid = 0;
    for(int i = 0; i < ARRAY_COUNT(processes); i++){
        pid = find_process_single(processes[i]);
        if(pid != 0){
            break;
        }
    }
    return pid;
}

DWORD find_process_single(const wchar_t* processName) {
    PROCESSENTRY32 processInfo;
    processInfo.dwSize = sizeof(processInfo);
    HANDLE processesSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
    if (processesSnapshot == INVALID_HANDLE_VALUE)
        return 0;
    Process32First(processesSnapshot, &processInfo);
    if (_wcsicmp(processName, processInfo.szExeFile) == 0)
    {
        CloseHandle(processesSnapshot);
        return processInfo.th32ProcessID;
    }
    while (Process32Next(processesSnapshot, &processInfo))
    {
        if (_wcsicmp(processName, processInfo.szExeFile) == 0)
        {
            CloseHandle(processesSnapshot);
            return processInfo.th32ProcessID;
        }
    }
    CloseHandle(processesSnapshot);
    return 0;
}
