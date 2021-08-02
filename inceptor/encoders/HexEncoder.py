import base64
from binascii import hexlify, unhexlify

from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class HexEncoder(Encoder):
    def __init__(self):
        super().__init__()
        self.decoder_in = [str]
        self.decoder_out = [bytes]

    def encode(self, data):
        return hexlify(data).decode()

    def decode(self, data):
        return unhexlify(data)

    def supported_languages(self):
        return [Language.CSHARP, Language.CPP, Language.POWERSHELL]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__
        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("HexEncoder.Decode")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.POWERSHELL:

            module.call_component = CallComponent("Invoke-HexDecode")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.CPP:

            module.call_component = CallComponent("length = hex_decode(encoded, length);")
            module.components = [
                CodeComponent(code)
            ]

        return module
