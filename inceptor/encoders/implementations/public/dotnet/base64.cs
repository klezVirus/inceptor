public static class Base64Encoder
{
    public static byte[] Decode(string data)
    {
        return Convert.FromBase64String(data);
    }

    public static byte[] Decode(byte[] data)
    {
        return Convert.FromBase64String(System.Text.Encoding.UTF8.GetString(data));
    }
}