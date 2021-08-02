#define _CRT_SECURE_NO_WARNINGS
//####DEFINE####

#include <windows.h>
#include <processenv.h>
#include <stdio.h>
#include <stdlib.h>

//####USING####

//####CODE####


int main(int argc, char** argv)
{

    const unsigned char raw[] = ####SHELLCODE####;
    int length = sizeof(raw);

    unsigned char* encoded = (unsigned char*)malloc(sizeof(unsigned char)*length*2);
    memcpy(encoded, raw, length);

    //####CALL####

    unsigned char* decoded = encoded;

    const char* filename = //####FILE####

    printf("[*] Writing %d bytes to %s\n", length, filename);
    FILE* file = fopen(filename, "wb");
    fwrite(decoded, sizeof(unsigned char), length, file);
    fclose(file);

    return 0;
}