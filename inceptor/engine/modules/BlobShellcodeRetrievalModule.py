from binascii import hexlify

from engine.modules.ShellcodeRetrievalModule import ShellcodeRetrievalModule
from enums.Language import Language


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
