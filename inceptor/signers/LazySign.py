import shutil
import subprocess
import sys
import time
from datetime import timedelta, datetime

from cryptography import x509

from enums.Architectures import Arch
from signers.Signer import Signer
from utils.console import Console
from OpenSSL import crypto, SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class LazySign(Signer):
    def __init__(self, host='www.microsoft.com', port='443', arch=Arch.x64, verbose=False):
        super().__init__(host=host, port=port, arch=arch, verbose=verbose)
        self.makecert = str(self.config.get_path("DIRECTORIES", "libs").joinpath("makecert.exe"))
        self.pvk2pfx = str(self.config.get_path("DIRECTORIES", "libs").joinpath("pvk2pfx.exe"))
        self.signtool = str(self.config.get_path("SIGNERS", f"SIGNTOOL_{self.arch.value}"))
        self.password = self.config.get("SIGNING", "password")

    def make_cert(self, pvk_file, cer_file):

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, self.host)
        ])

        alt_names = [x509.DNSName(self.host)]

        san = x509.SubjectAlternativeName(alt_names)

        # path_len=0 means this cert can only sign itself, not other certs.
        basic_contraints = x509.BasicConstraints(ca=True, path_length=0)
        code_signing = x509.ExtendedKeyUsage(usages=[x509.OID_CODE_SIGNING])
        key_usage = x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            )
        now = datetime.utcnow()
        cert = (
            x509.CertificateBuilder()
                .subject_name(name)
                .issuer_name(name)
                .public_key(key.public_key())
                .serial_number(1000)
                .not_valid_before(now)
                .not_valid_after(now + timedelta(days=10 * 365))
                .add_extension(code_signing, False)
                .add_extension(key_usage, False)
                .sign(key, hashes.SHA256(), default_backend())
        )
        cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        with open(cer_file, "wb") as f:
            f.write(cert_pem)
        with open(pvk_file, "wb") as f:
            f.write(key_pem)

    def export_pfx(self, cer_file, pvk_file, pfx_file):
        with open(cer_file, "rb") as fin:
            pem_text = fin.read()
        with open(pvk_file, "rb") as fin:
            key_text = fin.read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, pem_text)
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_text)

        p12 = crypto.PKCS12()
        p12.set_certificate(cert)
        p12.set_privatekey(key)
        p12_text = p12.export()
        with open(pfx_file, "wb") as fout:
            fout.write(p12_text)

    def sign(self, signee, signed):
        cer_file = self.certificate_directory.joinpath(f"{self.host}.cer")
        pvk_file = self.certificate_directory.joinpath(f"{self.host}.pvk")
        pfx_file = self.certificate_directory.joinpath(f"{self.host}.pfx")
        shutil.copy(signee, signed)
        time.sleep(1)

        steps = [
            [
                "Signing binary with spoofed certificate",
                f"\"{self.signtool}\" sign /debug /f \"{str(pfx_file)}\" /t \"{Signer.TIMESTAMP_URL_T}\" \"{signee}\"",
                "Failed to sign binary"
            ],
        ]

        exit = False
        if self.verbose:
            Console.auto_line(f"[*] Generating self-signed certificate")
        self.make_cert(pvk_file=pvk_file, cer_file=cer_file)

        if self.verbose:
            Console.auto_line(f"[*] Exporting certificate in PFX format")
        self.export_pfx(pfx_file=pfx_file, pvk_file=pvk_file, cer_file=cer_file)

        for step in steps:
            if self.verbose:
                Console.auto_line(f"[*] {step[0]}")
            cmd = step[1]
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().rstrip()
                if self.config.get_boolean("DEBUG", "signers"):
                    Console.auto_line(output)
            except subprocess.CalledProcessError as e:
                Console.auto_line(f"[-] {e.stdout.decode()}")
                exit = True
                break
        cer_file.unlink(missing_ok=True)
        pvk_file.unlink(missing_ok=True)
        pfx_file.unlink(missing_ok=True)
        if exit:
            sys.exit(1)
