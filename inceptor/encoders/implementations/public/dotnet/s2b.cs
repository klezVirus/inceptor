class S2bEncoder
{
    public static string Decode(byte[] data)
    {
        return System.Text.Encoding.UTF8.GetString(data);
    }
}
