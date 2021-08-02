import base64
import secrets
import string
import struct
from binascii import hexlify
from itertools import islice, cycle

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class AesEncryptor(Encoder):
    def __init__(self):
        super().__init__()
        self.decoder_in = [bytes]
        self.decoder_out = [bytes]
        self.key = ''.join(secrets.choice(".+-,:;_%=()" + string.ascii_letters + string.digits) for _ in range(36)).encode()
        self.salt = ''.join(secrets.choice(".+-,:;_%=()" + string.ascii_letters + string.digits) for _ in range(18)).encode()
        self.derived_key = PBKDF2(self.key.decode(), self.salt, 32, 1000)
        self.iv = PBKDF2(self.key.decode(), self.salt, 48, 1000)[32:]

    @property
    def c_key(self):
        k = hexlify(self.derived_key).decode()
        return ",".join([f"0x{k[i:i+2]}" for i in range(0, len(k), 2)])

    @property
    def c_iv(self):
        k = hexlify(self.iv).decode()
        return ",".join([f"0x{k[i:i+2]}" for i in range(0, len(k), 2)])

    def encode(self, data):
        if not isinstance(data, bytes):
            data = data.encode()
        cipher = AES.new(self.derived_key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
        return encrypted

    def decode(self, data):
        cipher = AES.new(self.derived_key, AES.MODE_CBC, self.iv)
        return unpad(cipher.decrypt(data), AES.block_size)

    def supported_languages(self):

        return [Language.CSHARP, Language.POWERSHELL, Language.CPP]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__

        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("AesEncryptor.Decrypt")
            module.components = [
                UsingComponent("System.Security.Cryptography", language=language),
                UsingComponent("System.IO", language=language),
                CodeComponent(code.replace("####KEY####", self.key.decode()).replace("####SALT####", self.salt.decode()))
            ]
        elif language == Language.CPP:
            module.call_component = CallComponent("length = aes_decrypt(encoded, length);")
            module.components = [
                UsingComponent("<string.h>", language=language),
                UsingComponent("<stdint.h>", language=language),
                UsingComponent("<stddef.h>", language=language),
                DefineComponent(r"""#define CBC 1
                #define AES256 1
                
                #define AES_BLOCKLEN 16
                #define AES_KEYLEN 32
                #define AES_keyExpSize 240
                #define Nk 8        
                #define Nr 14
                #define Nb 4
                
                #ifndef MULTIPLY_AS_A_FUNCTION
                  #define MULTIPLY_AS_A_FUNCTION 0
                #endif
                """, language=language),
                CodeComponent(code.replace("####KEY####", self.c_key).replace("####IV####", self.c_iv)
                )
            ]
        elif language == Language.POWERSHELL:
            module.call_component = CallComponent("Invoke-AesDecrypt")

            module.components = [
                CodeComponent(code.replace("####KEY####", self.key.decode()).replace("####SALT####", self.salt.decode()))
            ]
        return module
