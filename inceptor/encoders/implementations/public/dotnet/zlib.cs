public static class ZlibEncoder
{
    public static byte[] Decode(byte[] data)
    {
        return Ionic.Zlib.ZlibStream.UncompressBuffer(data);
    }
}