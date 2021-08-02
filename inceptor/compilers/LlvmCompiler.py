import os
import re
import secrets
import subprocess

from compilers.Compiler import Compiler
from config.Config import Config


class LlvmCompiler(Compiler):

    def __init__(self, args=None, aargs=None, arch="x64"):
        self.config = Config()
        self.vcvarsall = self.config.get_path("COMPILERS", "VCVARSALL")
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)
        self.prefix_cmd = f'"{self.vcvarsall}" {self.arch}'

    def format_libraries(self, libraries: list = None):
        if not libraries or not isinstance(libraries, list):
            libraries = []
        libraries = libraries + self.std_library()
        return " ".join([f'"{lib}"' for lib in libraries])

    def std_library(self):
        return ["kernel32.lib",
                "user32.lib",
                "gdi32.lib",
                "winspool.lib",
                "comdlg32.lib",
                "advapi32.lib",
                "shell32.lib",
                "ole32.lib",
                "oleaut32.lib",
                "uuid.lib",
                "odbc32.lib",
                "odbccp32.lib"]

    def default_dll_args(self, outfile):
        default_cl_args = {
            "/permissive-": None,
            "/GS": None,
            "/GL": None,
            "/W3": None,
            "/Gy": None,
            "/Zi": None,
            "/Gm-": None,
            "/O2": None,
            "/sdl": None,
            "/Zc:inline": None,
            "/Zc:wchar_t": None,
            "/fp": "precise",
            "/D \"BUILD_DLL\"": None,
            "/D \"NDEBUG\"": None,
            "/D \"SAGAT_EXPORTS\"": None,
            "/D \"_WINDOWS\"": None,
            "/D \"_WINDLL\"": None,
            "/D \"_USRDLL\"": None,
            "/D \"_UNICODE\"": None,
            "/D \"UNICODE\"": None,
            "/errorReport": "prompt",
            "/WX-": None,
            "/Zc": "forScope",
            "/Gd": None,
            "/Oi": None,
            "/MD": None,
            "/FC": None,
            "/EHsc": None,
            "/nologo": None,
            "/diagnostics": "column",
            "/LD": None,
            f'-o "{outfile}"': None
        }
        self.args = {**default_cl_args, **self.llvm_args()}

    def default_exe_args(self, outfile):
        default_cl_args = {
            "/permissive-": None,
            "/GS": None,
            "/GL": None,
            "/W3": None,
            "/Gy": None,
            "/Zi": None,
            "/Gm-": None,
            "/O2": None,
            "/sdl": None,
            "/Zc:inline": None,
            "/Zc:wchar_t": None,
            "/fp": "precise",
            "/D \"NDEBUG\"": None,
            "/D \"_CONSOLE\"": None,
            "/D \"_UNICODE\"": None,
            "/D \"UNICODE\"": None,
            "/errorReport": "prompt",
            "/WX-": None,
            "/Zc": "forScope",
            "/Gd": None,
            "/Oi": None,
            "/MD": None,
            "/FC": None,
            "/EHsc": None,
            "/nologo": None,
            "/diagnostics": "column",
            f'-o "{outfile}"': None
        }
        self.args = {**default_cl_args, **self.llvm_args()}

    def add_include_directory(self, directory):
        self.args[f'/I "{directory}"'] = None

    def set_libraries(self, libs: list):
        self.set_linker_options(libraries=libs)

    def set_linker_options(self, outfile=None, libraries: list = None):
        self.aargs = f'/link /DYNAMICBASE {self.format_libraries(libraries=libraries)}'
        if outfile:
            self.aargs += f' /OUT "{outfile}"'

    def llvm_args(self):
        return {
            "/D __CUDACC__": None,
            "/D _ALLOW_COMPILER_AND_STL_VERSION_MISMATCH": None,
            "-mllvm -bcf": None,
            "-mllvm -bcf_prob=73": None,
            "-mllvm -bcf_loop=1": None,
            "-mllvm -sub": None,
            "-mllvm -sub_loop=5": None,
            "-mllvm -fla": None,
            "-mllvm -split_num=5": None,
            f"-mllvm -aesSeed={secrets.token_hex(16)}": None,
            "-w": None
        }
