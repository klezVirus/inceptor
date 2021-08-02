import os
import re
import subprocess
import sys
import traceback
from abc import ABC, abstractmethod
from pydoc import locate

from config.Config import Config
from enums.Language import Language
from utils.console import Console
from utils.utils import get_project_root


class MissingArgumentException(Exception):
    pass


class ObfuscatorException(Exception):
    pass


class Obfuscator(ABC):

    def __init__(self, path: str = None, args: dict = None, sep=":"):
        self.name = self.__class__.__name__
        self.path = path
        self.args = args
        self.sep = sep
        self.debug = Config().get_boolean("DEBUG", "obfuscators")

    @staticmethod
    def from_name(name: str, language: Language, **kwargs):
        clazz = "dotnet"
        if language == language.POWERSHELL:
            clazz = "powershell"
        try:
            obfuscator_class_string = f"obfuscators.{clazz}.{name}.{name}"
            # print(obfuscator_class_string)
            obfuscator_class = locate(obfuscator_class_string)
            # print(obfuscator_class)
            obfuscator_instance = obfuscator_class(kwargs=kwargs['kwargs'])
            return obfuscator_instance
        except:
            traceback.print_exc()
            pass

    @abstractmethod
    def obfuscate(self):
        pass

    @staticmethod
    def choose_obfuscator(language, **kwargs):
        base_path = ""
        if language == Language.POWERSHELL:
            base_path = os.path.join(get_project_root(), Config().get("OBFUSCATORS", "powershell"))
        elif language == Language.CSHARP:
            base_path = os.path.join(get_project_root(), Config().get("OBFUSCATORS", "dotnet"))
        obfuscators = [
            os.path.splitext(f)[0] for f in os.listdir(base_path)
            if os.path.isfile(os.path.join(base_path, f))
            and os.path.splitext(f)[1] == ".py"
            and os.path.splitext(os.path.basename(f))[0] != "__init__"
        ]

        if len(obfuscators) > 1:
            try:
                Console.auto_line("  [#] Multiple obfuscators identified, choose one:")
                choice = -2
                for n, t in enumerate(obfuscators, start=0):
                    Console.auto_line(f"  {n}: {t}")
                while not 0 <= choice <= len(obfuscators) - 1:
                    try:
                        choice = int(input("  $> "))
                    except ValueError:
                        continue
            except KeyboardInterrupt:
                Console.auto_line("[-] Aborting")
                sys.exit(1)
        else:
            choice = 0
        return Obfuscator.from_name(name=str(obfuscators[choice]), language=language, kwargs=kwargs)

    def normalise_args(self):
        args = ""
        for k in self.args.keys():
            args += f" {k}{self.sep}{self.args[k]}" if self.args[k] is not None else f" {k}"
        return args
