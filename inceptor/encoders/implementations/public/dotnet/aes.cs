public static class AesEncryptor
{
    public static byte[] Decrypt(byte[] cipherBytes, string DecryptionKey = "####KEY####")
    {
        byte[] clearBytes;
        using (Aes encryptor = Aes.Create())
        {
            Rfc2898DeriveBytes pdb = new Rfc2898DeriveBytes(
                DecryptionKey,
                System.Text.Encoding.UTF8.GetBytes("####SALT####")
            );
            encryptor.Key = pdb.GetBytes(32);
            encryptor.IV = pdb.GetBytes(16);
            encryptor.Padding = PaddingMode.None;
            using (MemoryStream ms = new MemoryStream())
            {
                using (CryptoStream cs = new CryptoStream(ms, encryptor.CreateDecryptor(), CryptoStreamMode.Write))
                {
                    cs.Write(cipherBytes, 0, cipherBytes.Length);
                    cs.Close();
                }
                clearBytes = ms.ToArray();
            }
        }
        return clearBytes;
    }
}