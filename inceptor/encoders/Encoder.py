import sys
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from config.Config import Config
from engine.modules.EncoderModule import EncoderModule
from enums.Architectures import Arch
from enums.Language import Language
from utils.console import Console


class EncoderTypes(Enum):
    OBFUSCATOR = "Obfuscator"
    ENCRYPTOR = "Encryptor"
    ENCODER = "Encoder"

    @staticmethod
    def to_list():
        return [e.value for e in list(EncoderTypes)]


class Encoder(ABC):

    def __init__(self, order=None):
        self.implementations_dir: Path = Config().get_path("DIRECTORIES", "encoders")
        self.decoder_in = None
        self.decoder_out = None
        self.order = order
        pass

    def set_order(self, order):
        self.order = order

    @abstractmethod
    def encode(self, data):
        pass

    @abstractmethod
    def decode(self, data):
        pass

    @abstractmethod
    def translate(self, language=None, arch=Arch.x64) -> EncoderModule:
        pass

    @abstractmethod
    def supported_languages(self) -> list:
        pass

    def template(self, language: Language):
        base = ""
        ext = ""
        encoder = self.__class__.__name__.lower().replace('encoder', '').replace('encryptor', '')
        if language == Language.CSHARP:
            base = "dotnet"
            ext = ".cs"
        elif language == Language.CPP:
            base = "native"
            ext = ".cpp"
        elif language == Language.POWERSHELL:
            base = "powershell"
            ext = ".ps1"
        source = self.implementations_dir.joinpath(base).joinpath(
            f"{encoder}{ext}")

        if not source.exists():
            Console.auto_line(f"[-] {encoder} not supported in {language.name}")
            sys.exit(1)
        return open(str(source)).read()

    def is_supported(self, language):
        return language in self.supported_languages()
