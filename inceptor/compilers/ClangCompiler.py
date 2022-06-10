import os
import re
import subprocess

from compilers.Compiler import Compiler
from compilers.CompilerExceptions import OperationNotSupported
from config.Config import Config


class ClangCompiler(Compiler):

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

    def set_exports(self, exports):
        self.set_linker_options(other=f'/DEF:"{os.path.abspath(exports)}"')

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
            "-w": None,
            f'-o "{outfile}"': None
        }
        self.args = default_cl_args

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
            "-w": None,
            f'-o "{outfile}"': None
        }
        self.args = default_cl_args

    def default_obj_args(self, outfile):
        self.args = {
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
            "/c": None,
            f'/Fo"{outfile}"': None
        }

    def add_include_directory(self, directory):
        self.args[f'/I "{directory}"'] = None

    def hide_window(self):
        dll = "/D \"BUILD_DLL\""
        console = "/D \"_CONSOLE\""
        if console in self.args.keys():
            self.args.pop(console)
            self.set_linker_options(other="/SUBSYSTEM:windows /ENTRY:mainCRTStartup")
        elif dll in self.args.keys():
            raise OperationNotSupported(
                "DLLs don't support hidden windows at compiler level. Consider using SW_HIDE in the template"
            )
        return True

    def set_linker_options(self, outfile=None, libraries: list = None, other=""):
        if self.aargs is None or self.aargs == "":
            self.aargs = f'/link '
        elif not self.aargs.startswith("/link"):
            self.aargs = f'/link {self.aargs}'
        if libraries:
            self.aargs = f' /DYNAMICBASE {self.format_libraries(libraries=libraries)}'
        if outfile:
            self.aargs += f' /OUT "{outfile}"'
        self.aargs += f" {other}"

    def set_libraries(self, libs: list):
        self.set_linker_options(libraries=libs)

    def set_debug(self):
        self.args["/DEBUG"] = "FULL"
