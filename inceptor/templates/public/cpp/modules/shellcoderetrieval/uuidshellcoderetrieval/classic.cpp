#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define UUID_LENGTH 36


####RET#### ####FUNCTION####(####ARGS####)
{
    // UUIDs on the Heap
    char **new_uuids;
    // UUIDs on the Stack
    const char* uuids[] =
    {
        ####SHELLCODE####
    };

    int elems = sizeof(uuids) / sizeof(uuids[0]);

    // Let's create this list of UUIDs
    new_uuids = (char**) malloc(elems * sizeof(char*));

    for(int i = 0; i < elems; i++) {
       new_uuids[i] = (char*) malloc((UUID_LENGTH + 1) * sizeof(char));
       strcpy(new_uuids[i], uuids[i]);
    }
    return new_uuids;
}


