import os
import shutil
import sys
import tempfile

from config.Config import Config
from encoders.EncoderChain import EncoderChain
from engine.Filter import Filter
from engine.Template import Template
from engine.TemplateFactory import TemplateFactory
from engine.enums.Enums import LinkingMode
from engine.modules.AssemblyInfoModule import AssemblyInfoModule
from engine.modules.IShellcodeRetrievalModule import IShellcodeRetrievalModule
from engine.modules.ShellcodeRetrievalModule import ShellcodeRetrievalModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException, ModuleNotLoadableException, \
    ModuleNotFoundException
from enums.Architectures import Arch
from enums.Language import Language
from utils.console import Console


class CodeWriter:
    def __init__(self, file: str = None,
                 converter=None,
                 delay: int = None,
                 pinject: bool = False,
                 process: list = None,
                 language: Language = Language.CSHARP,
                 template: str = None,
                 _filter: Filter = None,
                 modules: list = None,
                 arch: str = "x64",
                 linking_mode: LinkingMode = LinkingMode.LIBRARY,
                 shellcode: bytes = None):
        self.debug = Config().get_boolean("DEBUG", "writer")
        self.additional_sources = []
        self.language = language

        dinvoke = len([m for m in modules if m.lower() == "dinvoke"]) > 0
        syscalls = len([m for m in modules if m.lower() == "syscalls"]) > 0

        self.arch = Arch.from_string(arch)
        kwargs = {
            "language": language,
            "seconds": delay,
            "dinvoke": dinvoke,
            "syscalls": syscalls,
            "process": process,
            "pinject": pinject,
            "arch": self.arch,
            "shellcode": shellcode,
            "linking_mode": linking_mode
        }

        modules_objects = []
        for m in modules:
            try:
                modules_objects.append(
                    TemplateModule.from_name(
                        name=m,
                        **kwargs
                    )
                )
            except ModuleNotCompatibleException as e:
                if self.debug:
                    Console.fail_line(f"[ERROR] Module {m} could not be loaded")
            except ModuleNotLoadableException as e:
                if self.debug:
                    Console.fail_line(f"[ERROR] Module {m} is not loadable")
            except ModuleNotFoundException as e:
                if self.debug:
                    Console.fail_line(f"[ERROR] Module {m} was not found")

        # SRM: Shellcode Retrieval Module
        # Every payload needs necessarily a way to retrieve the shellcode
        if not any([isinstance(m, IShellcodeRetrievalModule) for m in modules_objects]):
            modules_objects.append(
                TemplateModule.from_name(
                    name="blob_shellcode_retrieval",
                    **kwargs
                )
            )

        for m in modules_objects:
            if m and m.filter_string and m.filter_string != "":
                _filter.include.append(m.filter_string)
                _filter.imode = "and"

        if template:
            self.template = TemplateFactory.from_path(template, language=language, _filter=_filter)
        else:
            self.template = TemplateFactory.from_converter(
                file=file,
                dinvoke=dinvoke,
                syscalls=syscalls,
                pinject=pinject,
                converter=converter,
                language=language,
                _filter=_filter
            )
        ext = self.get_temporary_file_extension()

        self.load_modules(modules=modules_objects)

        # Dirty dirty workaround for DotNetToJScript
        if self.template.template_name.find("dtjs") > -1:
            self.load_module(TemplateModule.from_name("dtjs", kwargs=None), commit=True)

        working_directory = Config().get_path("DIRECTORIES", "WRITER")
        if working_directory and working_directory != "":
            self.outfile = tempfile.NamedTemporaryFile(dir=working_directory, delete=False, suffix=ext).name
        else:
            self.outfile = tempfile.NamedTemporaryFile(delete=False, suffix=ext).name

    @property
    def source_files(self):
        self.collect_sources()
        return [self.outfile] + self.additional_sources

    @property
    def resources(self):
        return self.collect_resources()

    def set_assembly_info(self, version_info):
        path = tempfile.NamedTemporaryFile(
            dir=str(Config().get_path("DIRECTORIES", "WRITER")),
            suffix=".cs",
            delete=True
        ).name
        if self.language == Language.CSHARP:
            description = version_info["FileDescription"] if "FileDescription" in version_info.keys() else ""
            copyright = version_info["LegalCopyright"] if "LegalCopyright" in version_info.keys() else ""
            company = version_info["CompanyName"] if "CompanyName" in version_info.keys() else ""
            product = version_info["ProductName"] if "ProductName" in version_info.keys() else ""
            file_version = version_info["FileVersion"] if "FileVersion" in version_info.keys() else ""
            assembly_version = version_info["ProductVersion"] if "ProductVersion" in version_info.keys() else ""
            title = version_info["OriginalFilename"] if "OriginalFilename" in version_info.keys() else ""

            self.load_module(
                AssemblyInfoModule(
                    path=path,
                    description=description,
                    copyright=copyright,
                    company=company,
                    product=product,
                    file_version=file_version,
                    assembly_version=assembly_version,
                    arch=self.arch,
                    title=description,
                    language=self.language
                )
            )

    def get_temporary_file_extension(self):
        if self.language == Language.CSHARP:
            return ".cs"
        elif self.language == Language.CPP:
            return ".cpp"
        elif self.language == Language.POWERSHELL:
            return ".ps1"

    def load_chain(self, chain: EncoderChain = None):
        if chain:
            self.template.load_chain(chain=chain)

    def load_modules(self, modules: list):
        for i in range(len(modules)):
            commit = (i == len(modules) - 1)
            self.load_module(modules[i], commit=commit)

    def load_module(self, module: TemplateModule, commit=False):
        if module:
            if self.debug:
                Console.auto_line(f"[DEBUG] Loading module {module.name}")
            self.template.add_module(module)
            for m in module.additional_modules:
                self.template.add_module(m)
        if commit:
            self.template.process_modules()

    def collect_sources(self):
        self.additional_sources = self.template.collect_sources()

    def collect_resources(self):
        return self.template.collect_resources()

    def write_source(self, shellcode):
        if not shellcode:
            return False
        content = ""
        try:
            content = self.template.generate(shellcode=shellcode)
        except Exception as e:
            print(f"[-] Exception in write_source while decoding template")
            print(f"[-] Exception: {e}")
            # traceback.print_exc()
            sys.exit(1)
        with open(self.outfile, "w") as out:
            out.write(content)

    def write(self, template: Template, outfile):
        raw = template.generate(shellcode=None)
        with open(outfile, "w") as out:
            out.write(raw)

    def clean(self, backup=False):

        if os.path.isfile(self.outfile):
            if backup:
                shutil.copy2(self.outfile, str(Config().get_path("DIRECTORIES", "backup")))
            os.unlink(self.outfile)
