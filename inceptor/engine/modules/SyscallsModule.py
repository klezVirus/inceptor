import os
import shutil
import sys
import tempfile

from compilers.ClCompiler import ClCompiler
from compilers.LibCompiler import LibCompiler
from compilers.MasmCompiler import MasmCompiler
from config.Config import Config
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.console import Console


class SyscallsModule(TemplateModule):
    def __init__(self, **kwargs):

        dinvoke = kwargs["kwargs"]["dinvoke"]
        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        self.arch = arch.value
        self.filter_string = "syscalls"
        libraries = []
        if language == Language.CPP:
            library = tempfile.NamedTemporaryFile(
                delete=True,
                dir=str(Config().get_path("DIRECTORIES", "WRITER")),
                suffix=".lib"
            ).name

            syscalls_basepath = tempfile.NamedTemporaryFile(
                delete=False,
                dir=str(Config().get_path("DIRECTORIES", "WRITER"))
            ).name

            headers = [f"{syscalls_basepath}.h"]

            kwargs = {
                "syscalls_path": syscalls_basepath,
                "dll": library,
                "arch": self.arch
            }
            self.generate(kwargs=kwargs)
            self.build(kwargs=kwargs)
            components = [
                UsingComponent(code=f'"{header}"', language=language) for header in headers
            ]
            libraries = [library]
        elif language == Language.CSHARP:
            if not dinvoke:
                Console.auto_line(f"[-] {self.__class__.__name__} requires -m dinvoke!")
                sys.exit(1)
            components = []
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="Syscalls", libraries=libraries, components=components, arch=arch)

    def generate(self, **kwargs):
        syswhisper_version = Config().get_int("SYSCALLS", "syswhispers")
        syscalls_basepath = kwargs["kwargs"]["syscalls_path"]

        if syswhisper_version == 1 and kwargs["kwargs"]["arch"] != "x64":
            Console.fail_line(f'[-] Syswhisper v1 does not support {kwargs["kwargs"]["arch"]}')
            sys.exit(1)
        elif syswhisper_version == 1:
            from syscalls.syswhispers.syswhispers import SysWhispers
        elif syswhisper_version == 2 and kwargs["kwargs"]["arch"] != "x64":
            from syscalls.syswhispersv2_x86.syswhispers import SysWhispers
        else:
            from syscalls.syswhispersv2.syswhispers import SysWhispers

        whispers = SysWhispers()
        whispers.generate(basename=syscalls_basepath)

    def build(self, **kwargs):
        syscalls_basepath = kwargs["kwargs"]["syscalls_path"]
        obj_files = [f"{syscalls_basepath}.0.obj"]

        masm = MasmCompiler(arch=self.arch)
        masm.default_args(outfile=obj_files[0])

        masm.compile([f"{syscalls_basepath}.asm"])
        if not os.path.isfile(f"{syscalls_basepath}.0.obj"):
            Console.auto_line("[-] Failed to compile syscall ASM stubs")
            sys.exit(1)

        # SysWhisper2 Only
        if os.path.isfile(f"{syscalls_basepath}.c"):
            obj_files.append(f"{syscalls_basepath}.1.obj")
            cl = ClCompiler(arch=self.arch)
            cl.default_obj_args(outfile=obj_files[1])
            cl.add_include_directory(str(Config().get_path("DIRECTORIES", "WRITER")))
            cl.compile([f"{syscalls_basepath}.c"])
            if not os.path.isfile(f"{syscalls_basepath}.1.obj"):
                Console.auto_line("[-] Failed to compile syscall C definitions")
                sys.exit(1)

        libc = LibCompiler(arch=self.arch)
        libc.default_args(kwargs["kwargs"]["dll"])
        libc.compile(obj_files)
