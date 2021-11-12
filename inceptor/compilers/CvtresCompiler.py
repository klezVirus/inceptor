import os
import re
import subprocess

from compilers.Compiler import Compiler
from config.Config import Config


class CvtresCompiler(Compiler):

    def __init__(self, args=None, aargs=None, arch="x64"):
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)

    def default_args(self, outfile):
        self.args = {
            "/NOLOGO": None,
            f'/OUT': f'"{outfile}"',
            f'/MACHINE': f'"{self.arch}"'
        }

    def add_include_directory(self, directory):
        self.args[f"/i\"{directory}\""] = None

    def set_libraries(self, libs: list):
        pass
