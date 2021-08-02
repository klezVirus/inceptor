class NopEncoder
{
    public static byte[] Decode(byte[] data)
    {
        int buf_len = data.Length/2 + 1;
        if (data.Length % 2 == 0){
            buf_len = data.Length/2;
        }
        byte[] decode = new byte[buf_len];
        int real_length = 0;
        for (int i=0; i<data.Length; i++){
            if (i % 2 == 0){
                decode[real_length] = data[i];
                real_length++;
            }
        }
        return decode;
    }
}
