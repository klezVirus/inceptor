class RunLengthEncoder
{
    public static string Decode(string data)
    {
        string decode = string.Empty;
        string[] pairs = data.Split(':');

        int index = 0;
        foreach (string s in pairs)
        {
            if (index % 100000 == 0){
                Console.Write("\r[*] Progress: {0}%            ", index*100/pairs.Length);
            }
            char original = s[s.Length - 1];
            int repeat = Int32.Parse(s.Remove(s.Length - 1));
            decode += new String(original, repeat);
            index++;
        }
        Console.WriteLine("\r[*] Progress: 100%");
        return decode;
    }
}
