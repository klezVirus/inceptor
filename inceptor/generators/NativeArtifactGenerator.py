import os
import shutil
import subprocess
import time
import traceback
from datetime import datetime

from compilers.Compiler import CompilerException, Compiler
from config.Config import Config
from converters.TransformerFactory import TransformerFactory
from encoders.EncoderChain import EncoderChain
from engine.CodeWriter import CodeWriter
from engine.Filter import Filter
from enums.Language import Language
from generators.Generator import Generator
from utils import CarbonCopy
from utils.console import Console
from utils.utils import shellcode_signature, py_bin2sh, sgn


class NativeArtifactGenerator(Generator):
    def __init__(self,
                 file: str = None,
                 chain: EncoderChain = None,
                 outfile: str = None,
                 dll: bool = False,
                 sgn: bool = False,
                 transformer=None,
                 pinject: bool = False,
                 process: str = None,
                 delay: int = None,
                 arch: str = None,
                 sign: bool = False,
                 obfuscate: bool = False,
                 exports: str = None,
                 compiler: str = "cl",
                 modules: list = None
                 ):
        super().__init__(file=file, chain=chain)
        self.arch = arch
        config = Config()
        self.placeholder = config.get("PLACEHOLDERS", "SHELLCODE")
        artifacts_path = config.get_path("DIRECTORIES", "ARTIFACTS")
        self.outfile = outfile

        # DLL Wrap generates a Write-Execute DLL
        self.dll_wrap = dll
        # DLL will generate a DLL instead of an exe (I might get rid of this distinction as it generates a bit of mess)
        self.dll = False
        if self.outfile.endswith("dll"):
            self.dll = True
        self.sgn = sgn
        self.sign = sign
        self.exports = exports
        self.obj_files = []

        if transformer:
            self.transformer = TransformerFactory.from_name(transformer)
        else:
            self.transformer = TransformerFactory.from_file(self.file)

        # EXE Writer
        self.exe_writer = CodeWriter(language=Language.CPP,
                                     pinject=pinject,
                                     process=process,
                                     delay=delay,
                                     modules=modules,
                                     _filter=Filter(exclude=["dll"]),
                                     arch=arch)
        self.exe_writer.load_chain(chain=self.chain)
        working_directory = Config().get_path("DIRECTORIES", "WRITER")

        basename = os.path.basename(os.path.splitext(outfile)[0])
        self.outfiles = {
            "exe-temp": os.path.join(working_directory, f"{basename}-temp.exe"),
            "dll-temp": os.path.join(working_directory, f"{basename}-temp.dll"),
            "exe": os.path.join(artifacts_path, "bison.exe"),
            "dll": os.path.join(artifacts_path, "sagat.dll"),
            "exe-signed": os.path.join(artifacts_path, f"{basename}-signed.exe"),
            "dll-signed": os.path.join(artifacts_path, f"{basename}-signed.dll"),
            "exe-final": outfile,
            "dll-final": f"{basename}.dll",
        }

        if obfuscate:
            compiler = "llvm"
        self.compiler = Compiler.from_name(compiler, args={}, arch=self.arch)
        self.compiler.default_exe_args(self.outfiles["exe-temp"])

        # DLL Writer
        self.dll_writer = None
        if self.dll:
            _dll_filter = Filter(include=["dll"], exclude=["write-execute"])

            self.dll_writer = CodeWriter(
                language=Language.CPP,
                template=config.get_path("DIRECTORIES", "DLL"),
                _filter=_dll_filter,
                modules=modules
            )
        elif self.dll_wrap:
            self.dll_writer = CodeWriter(
                language=Language.CPP,
                template=config.get_path("DIRECTORIES", "DLL"),
                _filter=Filter(include=["write-execute"]),
                modules=[]
            )
        self.dll_payload = None
        self.dll_compiler_args = self.compiler.default_dll_args(self.outfiles["dll-temp"])
        if self.exports and os.path.isfile(self.exports):
            self.dll_compiler_args["/DEF"] = f'"{os.path.abspath(self.exports)}"'

    def compile_dll(self, shellcode=None):
        if not shellcode:
            shellcode = self.dll_payload
        self.dll_writer.write_source(shellcode=shellcode)
        self.compiler.aargs = ""
        self.compiler.default_dll_args(outfile=self.outfiles["dll-temp"])
        self.compiler.compile([self.dll_writer.outfile])
        if not os.path.isfile(self.outfiles["dll-temp"]):
            raise FileNotFoundError("Error generating DLL")

    def sign_exe(self):
        host = Config().get("SIGNING", "domain")
        signer = CarbonCopy.CarbonCopy(verbose=False, host=host)
        signer.sign(signee=self.outfiles["exe-temp"], signed=self.outfiles["exe-signed"])
        shutil.copy(self.outfiles["exe-signed"], self.outfiles['exe-temp'])
        self.dll_payload = py_bin2sh(self.outfiles["exe-temp"])

    def sign_dll(self):
        host = Config().get("SIGNING", "domain")
        signer = CarbonCopy.CarbonCopy(verbose=False, host=host)
        signer.sign(signee=self.outfiles["dll-temp"], signed=self.outfiles["dll-signed"])
        shutil.copy(self.outfiles["dll-signed"], self.outfiles['dll-temp'])

    def finalise_exe(self):
        file = self.outfiles["exe-final"]
        shutil.copy(self.outfiles['exe-temp'], file)
        if os.path.isfile(file):
            Console.auto_line(f"    [+] Success: file stored at {file}")
        return file

    def finalise_dll(self):
        file = self.outfiles["dll-final"]
        shutil.copy(self.outfiles['dll-temp'], file)
        if os.path.isfile(file):
            Console.auto_line(f"    [+] Success: file stored at {file}")
        return file

    def compile_exe(self, shellcode):
        self.exe_writer.write_source(shellcode=shellcode)
        self.exe_writer.template.process_modules()
        self.compiler.default_exe_args(self.outfiles["exe-temp"])
        self.compiler.set_libraries(libs=self.exe_writer.template.libraries)

        status = self.compiler.compile([self.exe_writer.outfile] + self.obj_files)

        if not os.path.isfile(self.outfiles["exe-temp"]):
            raise FileNotFoundError("Error generating EXE")
        if not status:
            raise CompilerException("Compiler exited with errors")

        self.dll_payload = py_bin2sh(self.outfiles["exe-temp"])

    def clean(self):
        artifacts = [self.exe_writer.outfile]
        if self.dll:
            artifacts.append(self.dll_writer.outfile)
        for file in artifacts:
            os.unlink(file)
        base_paths = [".", "artifacts", "temp"]
        for base_path in base_paths:
            wildcards = [
                "tmp*",
                "*.cpp",
                "*.obj",
                "*.exp",
                "*.lib",
                "*.pdb",
                "*.shc.exe",
                "*.bin",
                "coded.txt",
                "*.obfuscated",
                "*.exe.config"
            ]
            if base_path == "temp":
                wildcards = ["*"]
            for wildcard in wildcards:
                subprocess.call(f"del /F /Q {os.path.join(base_path, wildcard)}",
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        for name, path in self.outfiles.items():
            if name.find("final") < 0:
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass

    def generate(self):
        try:
            self.generate_wrapped()
        except:
            traceback.print_exc()
            self.clean()

    def generate_wrapped(self):
        step = 0
        substep = 1
        artifact = None

        Console.auto_line(f"[+] Native Artifact Generator Started At {datetime.utcnow()}", )
        Console.auto_line(f"[*] Phase {step}: Loading...")
        step += 1
        if not self.chain.validate(language=Language.CPP):
            Console.auto_line("\n[-] ERROR: Failed to validate encoding chain")
            return

        Console.auto_line(f"[*] Phase {step}: Converting binary into shellcode")
        Console.auto_line(f"  [>] Transformer: {self.transformer.__class__.__name__}")
        shellcode_bytes = self.transformer.transform(target=self.file)
        step += 1
        Console.auto_line(f"[*] Phase {step}: Encoding")
        if self.sgn:
            Console.auto_line(f"  [>] Phase {step}.{substep}: Using Shikata-Ga-Nai {self.arch} to encode the shellcode")
            shellcode_bytes = sgn(shellcode_bytes, arch=self.arch)
            substep += 1
        if not self.chain.is_empty():
            Console.auto_line(f"  [>] Phase {step}.{substep}: Using Inceptor chained-encoder to encode the shellcode")
            Console.auto_line(f"  [>] Encoder Chain: {self.chain.to_string()}")
        shellcode = self.chain.encode(shellcode_bytes)
        step += 1
        template = self.exe_writer.template.template_name if not self.dll else self.dll_writer.template.template_name
        Console.auto_line(f"[*] Phase {step}: Generating source files using {template}")
        Console.auto_line(f"  [>] Phase {step}.{substep}: Writing CPP file in .\\temp\\{os.path.basename(self.exe_writer.outfile)}")
        time.sleep(1)
        step += 1
        if not self.dll:
            Console.auto_line(f"[*] Phase {step}: EXE compilation and Signing")
            Console.auto_line(f"  [>] Phase {step}.{substep}: Compiling EXE...")
            self.compile_exe(shellcode)
            substep += 1
            Console.auto_line(f"    [+] Success: file stored at {self.outfile}")
            Console.auto_line(f"    [+] Shellcode Signature: {shellcode_signature(shellcode)}")
            if self.sign:
                Console.auto_line(f"  [>] Phase {step}.{substep}: Signing native binary")
            step += 1
            substep = 1
        if self.dll or self.dll_wrap:
            Console.auto_line(f"[*] Phase {step}: DLL compilation and Signing")
            Console.auto_line(f"  [>] Phase {step}.{substep}: Compiling DLL...")
            self.compile_dll(shellcode if not self.dll_wrap else None)
            Console.auto_line(f"    [+] Success: file stored at {self.outfiles['dll-temp']}")
            substep += 1
            if self.sign:
                Console.auto_line(f"  [>] Phase {step}.2: Signing native library")
                self.sign_dll()
            step += 1
        substep = 1
        Console.auto_line(f"[*] Phase {step}: Finalising")
        if not self.dll:
            Console.auto_line(f"  [>] Phase {step}.{substep}: Finalising native binary")
            artifact = self.finalise_exe()
            substep += 1
        if self.dll or self.dll_wrap:
            Console.auto_line(f"  [>] Phase {step}.{substep}: Finalising native library")
            self.finalise_dll()
        step += 1
        Console.auto_line(f"[*] Phase {step}: Cleaning up...")
        self.clean()
        Console.auto_line(f"[+] Native Artifact Generator Finished At {datetime.utcnow()}")
        return artifact
