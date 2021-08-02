import base64
import secrets
import string
import struct
from itertools import islice, cycle

from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language
from Crypto.Util import strxor


class XorEncoder(Encoder):
    def __init__(self):
        super().__init__()
        self.decoder_in = [bytes]
        self.decoder_out = [bytes]
        self.key = ''.join(secrets.choice(".+-,:;_%=()" + string.ascii_letters + string.digits) for _ in range(12)).encode()

    def slow_encode(self, data):
        encoded = b""
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        for i in range(len(data)):
            print(f"    [>] Progress: {i * 100 / (len(data) - 1):.2f}%     ", end='\r')
            encoded += struct.pack("B", (data[i] ^ (self.key[i % len(self.key)])))
        print()
        return encoded

    def encode(self, data):
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        return strxor.strxor(data, bytearray(islice(cycle(self.key), len(data))))

    def supported_languages(self):
        return [Language.CSHARP, Language.CPP, Language.POWERSHELL]

    def decode(self, data):
        return self.encode(data)

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__
        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("XorEncoder.Decode")
            module.components = [
                CodeComponent(code.replace("####KEY####", self.key.decode()))
            ]
        elif language == Language.CPP:
            module.call_component = CallComponent("length = xor_encode(encoded, length);")
            module.components = [
                CodeComponent(code.replace("####KEY####", self.key.decode()).replace("####KEY_LENGTH####", str(len(self.key))))
            ]
        elif language == Language.POWERSHELL:
            module.call_component = CallComponent("Invoke-Xor")
            module.components = [
                CodeComponent(code.replace("####KEY####", self.key.decode()))
            ]
        return module
