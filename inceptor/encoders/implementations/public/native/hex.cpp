int hex_char_decode(const char hex, char *out)
{
    if (out == NULL)
        return 0;

    if (hex >= '0' && hex <= '9') {
        *out = hex - '0';
    } else if (hex >= 'A' && hex <= 'F') {
        *out = hex - 'A' + 10;
    } else if (hex >= 'a' && hex <= 'f') {
        *out = hex - 'a' + 10;
    } else {
        return 0;
    }

    return 1;
}

int hex_decode(unsigned char *encoded, int length)
{
    int len;
    char   b1;
    char   b2;
    int i;

    if (encoded == NULL || *encoded == '\0'){
        printf("Encoded is NULL\n");
        return 0;
    }
    len = length;
    if (len % 2 != 0){
        len--;
    }
    len /= 2;

    for (i=0; i<len; i++) {
        if (!hex_char_decode(encoded[i*2], &b1) || !hex_char_decode(encoded[i*2+1], &b2)) {
            return 0;
        }
        encoded[i] = (b1 << 4) | b2;
    }
    return len;
}
