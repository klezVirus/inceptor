public static class XorEncoder
{
    public static byte[] Decode(byte[] data)
    {
        byte[] decoded = new byte[data.Length];
        byte[] key = System.Text.Encoding.UTF8.GetBytes("####KEY####");
        for (int i = 0; i < data.Length; i++)
        {
            decoded[i] = (byte)(data[i] ^ key[i % key.Length]);
        }
        return decoded;
    }

}
