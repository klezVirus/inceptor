import base64

from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class Base64Encoder(Encoder):
    def __init__(self):
        super().__init__()
        self.decoder_in = [str, bytes]
        self.decoder_out = [bytes]

    def encode(self, data):
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        return base64.b64encode(data).decode()

    def decode(self, data):
        return base64.b64decode(data)

    def supported_languages(self):
        return [Language.CSHARP, Language.CPP, Language.POWERSHELL]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__

        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("Base64Encoder.Decode")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.POWERSHELL:

            module.call_component = CallComponent("Invoke-Base64Decode")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.CPP:

            module.call_component = CallComponent("length = base64_decode(encoded, length);")
            module.components = [
                UsingComponent("<string.h>", language=language),
                UsingComponent("<stdint.h>", language=language),
                UsingComponent("<stddef.h>", language=language),
                CodeComponent(code)
            ]

        return module
