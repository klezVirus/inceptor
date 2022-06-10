import os
import re
import subprocess
from pathlib import Path

from keystone import *


from compilers.Compiler import Compiler
from config.Config import Config
from keystone.keystone import Ks


class KeystoneCompiler(Compiler):
    def __init__(self, args=None, aargs=None, arch="x64"):
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)
        self.outfile = None

    def default_args(self, outfile=None):
        self.outfile = outfile

    def add_include_directory(self, directory):
        pass

    def set_libraries(self, libs: list):
        pass

    def set_debug(self):
        pass

    def format(self, content):
        return "".join(
            [
                re.search(r"[^;]+", line).group(0) + ";" for line in content.split("\n")
                if not line.strip().startswith(";") and not line.strip() == ""
            ]
        )

    def compile(self, files: list):
        ks = Ks(KS_ARCH_X86, KS_MODE_32 if self.arch == "x86" else KS_MODE_64)
        for f in files:
            basename = os.path.splitext(f)[0]
            with open(f, "r") as assembly:
                code = self.format(assembly.read())
                shellcode, n = ks.asm(code)
                with open(f"{basename}.obj", "wb") as obj:
                    obj.write(shellcode)
            break
        return shellcode

