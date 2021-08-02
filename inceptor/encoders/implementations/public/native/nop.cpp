int nop_decode(unsigned char* encoded, int length)
{
    int data_len = 0;
    for (int i = 0; i < length; i++) {
        if (i % 2 == 0){
            encoded[data_len] = encoded[i];
            data_len++;
        }
    }
    return data_len;
}