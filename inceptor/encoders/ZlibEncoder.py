import base64
import codecs
import os

from config.Config import Config
from encoders.Encoder import Encoder
from engine.component.CallComponent import CallComponent
from engine.component.CodeComponent import CodeComponent
from engine.modules.EncoderModule import EncoderModule
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class ZlibEncoder(Encoder):
    def __init__(self):
        super().__init__()
        self.decoder_in = [bytes]
        self.decoder_out = [bytes]

    def encode(self, data):
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        compressed = codecs.encode(data, 'zlib')
        return compressed

    def decode(self, data):
        return data.decode('zlib')

    def supported_languages(self):
        return [Language.CSHARP]

    def translate(self, language=Language.CSHARP, arch=Arch.Any):
        module = EncoderModule()
        code = self.template(language=language)
        if language == Language.CSHARP:

            module.name = self.__class__.__name__
            module.call_component = CallComponent("ZlibEncoder.Decode")
            module.libraries = [str(Config().get_path("DIRECTORIES", "libs").joinpath(arch.value, "Zlib.Portable.dll"))]
            module.components = [
                CodeComponent(code)
            ]
        return module
