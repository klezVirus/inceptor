import os

from converters import Transformer
from converters.Donut import Donut
from converters.Loader import Loader
from converters.Pe2Shellcode import Pe2sh
from converters.sRDI import sRDI
from utils.utils import isDotNet


class TransformerFactory:

    @staticmethod
    def allowed(file) -> list:
        filename, ext = os.path.splitext(file)
        allowed_list = []
        if ext == ".exe":
            if isDotNet(file):
                allowed_list = [Loader, Donut]
            else:
                allowed_list = [Loader, Pe2sh, Donut]
        elif ext == ".dll":
            allowed_list = [sRDI]
        if ext == ".raw":
            allowed_list = [Loader]
        return [c().__class__.__name__.lower() for c in allowed_list]

    @staticmethod
    def from_file(file) -> Transformer:
        filename, ext = os.path.splitext(file)
        if ext == ".exe":
            if isDotNet(file):
                return Donut()
            else:
                return Pe2sh()
        elif ext == ".dll":
            return sRDI()
        if ext == ".raw":
            return Loader()

    @staticmethod
    def from_name(name) -> Transformer:
        if name == "loader":
            clazz = Loader
        elif name == "srdi":
            clazz = sRDI
        elif name == "pe2sh":
            clazz = Pe2sh
        elif name == "donut":
            clazz = Donut
        else:
            raise NotImplementedError(f"No transformer for class {name}")
        return clazz()
