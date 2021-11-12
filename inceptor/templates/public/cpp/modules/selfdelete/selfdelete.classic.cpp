#include <windows.h>
#include <shlwapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <winternl.h>

#pragma warning(disable:4996)

#define NEW_ADS L":####ADS####"

BOOL rename_data_stream(HANDLE);
BOOL mark_for_deletion(HANDLE);

BOOL debug = false;

BOOL rename_data_stream(HANDLE hHandle)
{
    FILE_RENAME_INFO friRename;
    memset(&friRename, 0, sizeof(friRename));

    LPWSTR lpwStream = (LPWSTR)NEW_ADS;
    friRename.FileNameLength = sizeof(lpwStream);

    memcpy(friRename.FileName, lpwStream, sizeof(lpwStream));

    return SetFileInformationByHandle(hHandle, FileRenameInfo, &friRename, sizeof(friRename));
}


BOOL mark_for_deletion(HANDLE hHandle)
{
    FILE_DISPOSITION_INFO fDelete;
    memset(&fDelete, 0, sizeof(fDelete));

    fDelete.DeleteFile = TRUE;

    return SetFileInformationByHandle(hHandle, FileDispositionInfo, &fDelete, sizeof(fDelete));
}

int ####FUNCTION####()
{
    WCHAR wcPath[MAX_PATH + 1];
    memset(wcPath, 0, sizeof(wcPath));

    if (GetModuleFileNameW(NULL, wcPath, MAX_PATH) == 0) {
        printf("[-] %s\n", "Failed to get current module handle.");
        return 0;
    }
    else {
        if (debug) {
            printf("[+] %s\n", "Obtained a handle to current module file handle.");
            printf("[*] Current file path: %ls\n", (wchar_t*)wcPath);
        }
    }

    HANDLE hCurrent = CreateFileW(wcPath, DELETE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hCurrent == INVALID_HANDLE_VALUE) {
        if (debug) {
            printf("[-] %s\n", "Failed to get handle to current file.");
        }
        return 0;
    }
    else {
        if (debug) {
            printf("[+] %s\n", "Got handle to file.");
        }
    }

    BOOL returnedHandleRename = rename_data_stream(hCurrent);
    if (!returnedHandleRename) {
        if (debug) {
            printf("[-] %s\n", "Failed to rename data stream from handle.");
        }
        CloseHandle(hCurrent);
        return 0;
    }
    else {
        if (debug) {
            printf("[+] Renamed handle to %ls's data stream successfully.\n", (wchar_t*)wcPath);
        }
        CloseHandle(hCurrent);
    }

    hCurrent = CreateFileW(wcPath, DELETE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hCurrent == INVALID_HANDLE_VALUE) {
        if (debug) {
            printf("[-] %s\n", "Failed to get second handle to current file.");
        }
        return 0;
    }
    else {
        if (debug) {
            printf("[+] %s\n", "Got second handle to file for further manipulation.");
        }
    }

    if (!mark_for_deletion(hCurrent)) {
        if (debug) {
            printf("[-] %s\n", "Failed to set desired deposition. Destroying handle and returning.");
        }
        CloseHandle(hCurrent);

        return 0;
    }
    else {
        if (debug) {
            printf("[+] %s\n", "Deletion attribute set successfully! Destroying handle to trigger self-deletion");
        }
        CloseHandle(hCurrent);
    }
    return 0;
}