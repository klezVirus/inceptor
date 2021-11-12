#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winternl.h>
#include <windows.h>
//####USING####

####RET#### ####FUNCTION####(int* length)
{
	HRSRC res;
	HGLOBAL resHandle = NULL;
	unsigned char * payload;
	unsigned int payload_len;

	// Extract payload from resources section
	res = FindResource(NULL, MAKEINTRESOURCE(FAVICON_ICO), RT_RCDATA);
	resHandle = LoadResource(NULL, res);
	payload = (unsigned char *) LockResource(resHandle);
	*length = SizeofResource(NULL, res);
    int resSize = *length;
	unsigned char* array = (unsigned char*)malloc(sizeof(unsigned char)*resSize*2);

    memcpy(array, payload, resSize);
    // We finished copy our payload, we can free the resource now
    FreeResource(resHandle);
    return array;
}
