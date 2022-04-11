from enum import Enum


class Compiler(Enum):
    All = ""
    MSVC = "MSVC"
    MINGW = "MinGW"

    @staticmethod
    def from_string(label):
        if label.lower() in ["all"]:
            return Compiler.All
        elif label.lower() in ["msvc"]:
            return Compiler.MSVC
        elif label.lower() in ["mingw"]:
            return Compiler.MINGW
