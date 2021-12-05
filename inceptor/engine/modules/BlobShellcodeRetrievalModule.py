import os
from abc import ABC, abstractmethod
from binascii import hexlify

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.LibCompiler import LibCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.ShellcodeRetrievalModule import ShellcodeRetrievalModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root, get_temporary_file, static_random_ascii_string


class BlobShellcodeRetrievalModule(ShellcodeRetrievalModule):
    def __init__(self, **kwargs):
        while "kwargs" in kwargs.keys():
            kwargs = kwargs["kwargs"]
        kwargs["name"] = self.__class__.__name__
        super().__init__(**kwargs)

    def craft(self, shellcode, language) -> (str, list, str):
        if language == Language.CSHARP:
            if isinstance(shellcode, bytes):
                shellcode = hexlify(shellcode).decode()
                return "byte[]", [], "new byte[]{" + ",".join([f"0x{shellcode[i:i + 2]}" for i in range(0, len(shellcode), 2)]) + "}"
            # shellcode = "".join([f"\\x{shellcode[i:i + 2]}" for i in range(0, len(shellcode), 2)])
            return "string", [], f"\"{shellcode}\""
        elif language == Language.CPP:
            if isinstance(shellcode, bytes):
                shellcode = hexlify(shellcode).decode()
                shellcode = "{" + ",".join([f"0x{shellcode[i:i + 2]}" for i in range(0, len(shellcode), 2)]) + "}"
            if isinstance(shellcode, str):  # and not re.match(r"^(\\x[A-Fa-f0-9]{2})+$", shellcode):
                return "unsigned char*", [], shellcode
        elif language == Language.POWERSHELL:
            if isinstance(shellcode, bytes):
                shellcode = hexlify(shellcode).decode()
                return "[byte[]]", [], "@(" + ",".join([f"0x{shellcode[i:i + 2]}" for i in range(0, len(shellcode), 2)]) + ")"
            else:
                return "string", [], f"\"{shellcode}\""
