import os

from compilers.Compiler import Compiler
from config.Config import Config
from utils.utils import *


class ILPacker(Compiler):
    def add_include_directory(self, directory):
        pass

    def __init__(self, args=None, aargs=None):
        path = str(Config().get_path("DIRECTORIES", "libs").joinpath("ILRepack.exe"))
        if not os.path.isfile(path):
            raise FileNotFoundError("Missing Packer Executable")
        super().__init__(path, args=args, aargs=aargs, sep=":")

    def set_libraries(self, libs: list):
        pass
