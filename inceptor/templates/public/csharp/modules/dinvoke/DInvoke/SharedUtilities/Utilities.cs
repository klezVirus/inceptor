using System;
using System.Security.Cryptography.X509Certificates;

namespace DInvoke.Utilities
{
    class Utilities
    {
        /// <summary>
        /// Checks that a file is signed and has a valid signature.
        /// </summary>
        /// <param name="FilePath">Path of file to check.</param>
        /// <returns></returns>
        public static bool FileHasValidSignature(string FilePath)
        {
            X509Certificate2 FileCertificate;
            try
            {
                X509Certificate signer = X509Certificate.CreateFromSignedFile(FilePath);
                FileCertificate = new X509Certificate2(signer);
            }
            catch
            {
                return false;
            }

            X509Chain CertificateChain = new X509Chain();
            CertificateChain.ChainPolicy.RevocationFlag = X509RevocationFlag.EntireChain;
            CertificateChain.ChainPolicy.RevocationMode = X509RevocationMode.Offline;
            CertificateChain.ChainPolicy.VerificationFlags = X509VerificationFlags.NoFlag;

            return CertificateChain.Build(FileCertificate);
        }
    }
}
