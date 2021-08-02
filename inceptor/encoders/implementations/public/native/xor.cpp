int xor_encode(unsigned char* data, int data_len)
{
    const char* key = "####KEY####";
    int key_len = ####KEY_LENGTH####;

    for (int i = 0; i < data_len; i++){
        data[i] = (data[i] ^ (unsigned char)key[i % key_len]);
    }
    return data_len;
}