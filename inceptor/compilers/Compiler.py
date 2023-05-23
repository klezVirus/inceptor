import os
import re
import subprocess
import sys
import traceback
from abc import ABC, abstractmethod
from pydoc import locate

from config.Config import Config


class CompilerException(Exception):
    pass


class Compiler(ABC):

    def __init__(self, path: str = None, args: dict = None, sep=":", aargs=None, arch="x64"):
        self.name = self.__class__.__name__.upper().replace("COMPILER", "")
        self.arch = arch
        if arch == "anycpu":
            arch = "x86"
        if path:
            self.path = path
        else:
            self.path = Config().get("COMPILERS", f"{self.name}{arch}_COMPILER")
        self.prefix_cmd = None
        self.suffix_cmd = None
        self.args = args if args else {}
        self.aargs = ""
        self.sep = sep
        if aargs:
            self.aargs = aargs

    @abstractmethod
    def set_libraries(self, libs: list):
        pass

    def hide_window(self):
        return False

    @abstractmethod
    def add_include_directory(self, directory):
        pass

    def compile(self, files: list):
        file_arg = ""
        for file in files:
            if not os.path.isfile(file):
                print(f"[-] Compiler: File {file} not found")
            else:
                file_arg += f" \"{file}\""
        try:
            args = ""
            for k in self.args.keys():
                args += f" {k}{self.sep}{self.args[k]}" if self.args[k] is not None else f" {k}"
            cmd = f"\"{self.path}\" {args} {file_arg}"
            if self.aargs:
                cmd = f"{cmd} {self.aargs}"
            if self.prefix_cmd:
                cmd = f"{self.prefix_cmd} & {cmd}"
            if self.suffix_cmd:
                cmd = f"{cmd} & {self.suffix_cmd}"
            if Config().get_boolean("DEBUG", "COMPILERS"):
                print(cmd)
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if Config().get_boolean("DEBUG", "COMPILERS"):
                print(output.decode(errors="replace"))
        except subprocess.CalledProcessError as e:
            for line in e.output.decode(errors="replace").split("\n"):
                if re.search(r"error", line):
                    print(f"  [-] Error: {line}")
                    raise Exception("Compiler Error")
            return False
        return True

    @staticmethod
    def from_name(name: str, args=None, aargs=None, arch="x64"):
        try:
            obfuscator_class_string = f"compilers.{name.capitalize()}Compiler.{name.capitalize()}Compiler"
            # print(obfuscator_class_string)
            obfuscator_class = locate(obfuscator_class_string)
            # print(obfuscator_class)
            obfuscator_instance = obfuscator_class(args=args, aargs=aargs, arch=arch)
            return obfuscator_instance
        except:
            traceback.print_exc()
            pass
