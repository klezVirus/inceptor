import uuid
from binascii import unhexlify

from engine.modules.ShellcodeRetrievalModule import ShellcodeRetrievalModule
from engine.modules.TemplateModule import ModuleNotCompatibleException
from enums.Language import Language
from utils.console import Console


class UuidShellcodeRetrievalModule(ShellcodeRetrievalModule):
    def __init__(self, **kwargs):
        while "kwargs" in kwargs.keys():
            kwargs = kwargs["kwargs"]
            kwargs["name"] = self.__class__.__name__
        super().__init__(**kwargs)
        self.filter_string = "uuid"

    def craft(self, shellcode, language) -> (str, list, str):
        Console.warn_line("[WARNING] This module is only supported by 'uuid' based templates")
        Console.warn_line("[WARNING] This module is not compatible with LD encoders")
        data = shellcode
        if isinstance(shellcode, str):
            data = unhexlify(shellcode)
        if len(data) % 16 != 0:
            padding = b"\x90" * (16 - (len(data) % 16))
            data += padding
        uuids = []
        for i in range(0, len(data), 16):
            uuid_string = str(uuid.UUID(bytes_le=data[i:i + 16]))
            uuids.append(f'"{uuid_string}"')
        self.uuids = ",\n".join(uuids)
        self.shellcode_length = len(uuids)
        if language == Language.POWERSHELL:
            raise ModuleNotCompatibleException

        if language == Language.CSHARP:
            return "string[]", [], self.uuids
        elif language == Language.CPP:
            return "char**", [], self.uuids

