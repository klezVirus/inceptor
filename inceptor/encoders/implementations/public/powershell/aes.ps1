function Invoke-AesDecrypt
{
    [CmdletBinding()]
    param
    (
    [Parameter(Mandatory=$True)]
    [byte[]]$Encrypted,
    [Parameter(Mandatory=$False)]
    [string]$Key
    )

    $DecryptionKey = '####KEY####'

    if(-not([string]::IsNullOrEmpty($Key))){
        $DecryptionKey = $Key
    }

    $salt = [System.Text.Encoding]::UTF8.GetBytes("####SALT####");
    $pdb = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($DecryptionKey, $salt)

    $AESKey = $pdb.GetBytes(32);
    $AESIV = $pdb.GetBytes(16);
    $AES = New-Object Security.Cryptography.AesManaged
    $AES.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $AES.Padding = [System.Security.Cryptography.PaddingMode]::None
    $AES.BlockSize = 128
    $AES.KeySize = 256


    $ms = [System.IO.MemoryStream]::new()

    $cs = New-Object System.Security.Cryptography.CryptoStream(
        $ms,
        $AES.CreateDecryptor($AESKey, $AESIV),
        [System.Security.Cryptography.CryptoStreamMode]::Write
        );

    $cs.Write($Encrypted, 0, $Encrypted.Length)
    $cs.Close()
    $decrypted = $ms.ToArray()
    $ms.Dispose()

    return $decrypted;
}