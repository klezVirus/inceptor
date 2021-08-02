from binascii import hexlify, unhexlify

from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class NopEncoder(Encoder):
    """
    This encoder takes as input an hexlified version of the payload
    Then, it perform a NOP insertion byte per byte
    The resulting payload is duplicated in size

    Input String
    Output String
    """

    def __init__(self):
        super().__init__()
        self.decoder_in = [bytes]
        self.decoder_out = [bytes]

    def encode(self, data):
        if isinstance(data, bytes):
            data = hexlify(data).decode()
        data = "".join([f"{data[i:i + 2]}90" for i in range(0, len(data), 2)])
        return unhexlify(data)

    def decode(self, data):
        if isinstance(data, bytes):
            data = hexlify(data).decode()
        decoded = ""
        tokens = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(tokens)):
            if i % 2 == 0:
                decoded += tokens[i]
        return unhexlify(decoded)

    def supported_languages(self):
        return [Language.CSHARP, Language.CPP, Language.POWERSHELL]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__
        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("NopEncoder.Decode")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.CPP:
            module.call_component = CallComponent("length = nop_decode(encoded, length);")
            module.components = [
                CodeComponent(code)
            ]
        elif language == Language.POWERSHELL:
            module.call_component = CallComponent("Invoke-NopDecode")
            module.components = [
                CodeComponent(code)
            ]
        return module
