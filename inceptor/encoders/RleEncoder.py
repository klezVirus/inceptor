from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class RleEncoder(Encoder):

    def __init__(self):
        super().__init__()
        self.decoder_in = [str]
        self.decoder_out = [str]

    def encode(self, data):
        encoding = ''
        prev_char = ''
        count = 1

        if not data:
            return ''

        for char in data:
            if char != prev_char:
                if prev_char:
                    encoding += str(count) + prev_char + ":"
                count = 1
                prev_char = char
            else:
                count += 1
        encoding += str(count) + prev_char
        return encoding

    def decode(self, data):
        pairs = data.split(":")
        decode = ""
        for p in pairs:
            decode += p[-1] * int(p[:-1])
        return decode

    def supported_languages(self):
        return [Language.CSHARP]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__
        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("RunLengthEncoder.Decode")
            module.components = [
                CodeComponent(code)
            ]
        return module

