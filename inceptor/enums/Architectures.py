from enum import Enum


class Arch(Enum):
    Any = ""
    x86 = "x86"
    x64 = "x64"

    @staticmethod
    def from_string(label):
        if label.lower() in ["any"]:
            return Arch.Any
        elif label.lower() in ["32", "86", "x86", "i386"]:
            return Arch.x86
        elif label.lower() in ["64", "x64", "amd64", "x86_64"]:
            return Arch.x64
