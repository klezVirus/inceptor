#include <stdio.h>
#include <stdlib.h>
#include <string.h>

####RET#### ####FUNCTION####(####ARGS####)
{
    const unsigned char raw[] = ####SHELLCODE####;
    int length = sizeof(raw);

    unsigned char* array = (unsigned char*)malloc(sizeof(unsigned char)*length*2);

    memcpy(array, raw, sizeof(raw));
    return array;
}
