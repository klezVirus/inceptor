public static class HexEncoder
{
    public static byte[] Decode(string hex)
    {
        var chars = hex.ToCharArray();
        var bytes = new List<byte>();
        for(int index = 0; index < chars.Length; index += 2) {
            var chunk = new string(chars, index, 2);
            bytes.Add(byte.Parse(chunk, System.Globalization.NumberStyles.AllowHexSpecifier));
        }
        return bytes.ToArray();
    }
}
