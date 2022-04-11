import os
import shutil
import sys
import tempfile
import time

import in_place

from compilers.ClCompiler import ClCompiler
from compilers.LibCompiler import LibCompiler
from compilers.MasmCompiler import MasmCompiler
from config.Config import Config
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from enums.Architectures import Arch
from enums.SyscallRecoveryType import SyscallRecoveryType
from utils.console import Console


class SyscallsModule(TemplateModule):
    def __init__(self, **kwargs):

        while "kwargs" in kwargs.keys():
            kwargs = kwargs.get("kwargs")

        dinvoke = kwargs.get("dinvoke")
        language = kwargs.get("language")
        self.arch = kwargs.get("arch")

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
            ).name.replace("_", "a")

            headers = [f"{syscalls_basepath}.h"]

            kwargs = {
                "syscalls_path": syscalls_basepath,
                "dll": library,
                "arch": self.arch
            }
            _ = self.generate(**kwargs)
            self.build(**kwargs)
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
        super().__init__(name="Syscalls", libraries=libraries, components=components, arch=self.arch)

    def generate(self, **kwargs):
        debug = Config().get_boolean("DEBUG", "syswhispers")
        syswhisper_version = Config().get_int("SYSCALLS", "syswhispers")
        if debug:
            Console.warn_line(f"[DEBUG] Syswhisper version: V{syswhisper_version}")

        syscalls_basepath = kwargs.get("syscalls_path")
        recovery = SyscallRecoveryType.from_name_or_default(kwargs.get("recovery"))

        # SysWhispers3 is the definitive version of SysWhispers (at the moment xD)
        from syscalls.syswhispersv3.syswhispers import SysWhispers

        verbose = Config().get_boolean("DEBUG", "SYSWHISPERS")
        debug = Config().get_boolean("SYSCALLS", "debug")
        syscall_instruction = Config().get("SYSCALLS", "syscall_op_override")
        if not syscall_instruction or syscall_instruction == "":
            syscall_instruction = "syscall"
        whispers = SysWhispers(
            arch=self.arch,
            recovery=SyscallRecoveryType.JUMPER,
            syscall_instruction=syscall_instruction,
            wow64=False,
            verbose=verbose,
            debug=debug
        )
        while not os.path.isfile(f"{syscalls_basepath}-asm.{self.arch.value}.asm"):
            whispers.generate(basename=syscalls_basepath)
            time.sleep(1)

        if debug:
            input("Press a key to keep going")
        return None

    def build(self, **kwargs):
        syscalls_basepath = kwargs["syscalls_path"]
        obj_files = [f"{syscalls_basepath}.0.obj"]

        masm = MasmCompiler(arch=self.arch.value)
        masm.default_args(outfile=obj_files[0])

        masm.compile([f"{syscalls_basepath}-asm.{self.arch.value}.asm"])
        if not os.path.isfile(f"{syscalls_basepath}.0.obj"):
            Console.auto_line("[-] Failed to compile syscall ASM stubs")
            sys.exit(1)

        # SysWhisper2 Only
        if os.path.isfile(f"{syscalls_basepath}.c"):
            obj_files.append(f"{syscalls_basepath}.1.obj")
            cl = ClCompiler(arch=self.arch.value)
            cl.default_obj_args(outfile=obj_files[1])
            cl.add_include_directory(str(Config().get_path("DIRECTORIES", "WRITER")))
            cl.compile([f"{syscalls_basepath}.c"])
            if not os.path.isfile(f"{syscalls_basepath}.1.obj"):
                Console.auto_line("[-] Failed to compile syscall C definitions")
                sys.exit(1)

        libc = LibCompiler(arch=self.arch.value)
        libc.default_args(kwargs["dll"])
        libc.compile(obj_files)
