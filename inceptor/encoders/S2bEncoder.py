from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Language import Language


class S2bEncoder(Encoder):

    def __init__(self):
        super().__init__()
        self.decoder_in = [bytes]
        self.decoder_out = [str]

    def encode(self, data):
        return data

    def decode(self, data):
        return data

    def supported_languages(self):
        return [Language.CSHARP]

    def translate(self, language=Language.CSHARP, arch=None):
        module = EncoderModule()
        module.name = self.__class__.__name__
        code = self.template(language=language)

        if language == Language.CSHARP:
            module.call_component = CallComponent("S2bEncoder.Decode")
            module.components = [
                CodeComponent(code)
            ]
        return module

