from enum import Enum


class Language(Enum):
    CSHARP = 0
    CPP = 1
    POWERSHELL = 2

    @staticmethod
    def from_string(label):
        if label.lower() in ["c#", "csharp", "cs", ".cs"]:
            return Language.CSHARP
        elif label.lower() in ["c", ".c", "cpp", ".cpp", "c++"]:
            return Language.CPP
        elif label.lower() in ["ps", ".ps1", "powershell"]:
            return Language.POWERSHELL

