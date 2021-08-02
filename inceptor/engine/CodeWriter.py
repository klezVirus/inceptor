import os
import sys
import tempfile

from config.Config import Config
from encoders.EncoderChain import EncoderChain
from engine.Filter import Filter
from engine.Template import Template
from engine.TemplateFactory import TemplateFactory
from engine.modules.AssemblyInfoModule import AssemblyInfoModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException, ModuleNotLoadableException
from enums.Architectures import Arch
from enums.Language import Language
from utils.console import Console


class CodeWriter:
    def __init__(self, file: str = None,
                 converter=None,
                 delay: int = None,
                 pinject: bool = False,
                 process: str = None,
                 language: Language = Language.CSHARP,
                 template: str = None,
                 _filter: Filter = None,
                 modules: list = None,
                 arch: str = "x64"):
        self.additional_sources = []
        self.language = language
        self.bypass_dll = tempfile.NamedTemporaryFile(
            delete=True,
            dir=str(Config().get_path("DIRECTORIES", "WRITER")),
            suffix=".dll"
        ).name

        dinvoke = len([m for m in modules if m.lower() == "dinvoke"]) > 0
        syscalls = len([m for m in modules if m.lower() == "syscalls"]) > 0

        kwargs = {
            "language": language,
            "seconds": delay,
            "dinvoke": dinvoke,
            "syscalls": syscalls,
            "process": process,
            "pinject": pinject,
            "arch": Arch.from_string(arch)
        }

        modules_objects = []
        for m in modules:
            try:
                modules_objects.append(
                    TemplateModule.from_name(
                        name=m,
                        kwargs=kwargs
                    )
                )
            except ModuleNotCompatibleException as e:
                Console.auto_line(f"[-] Module {m} could not be loaded")
            except ModuleNotLoadableException as e:
                Console.auto_line(f"[-] Module {m} is not loadable")

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

        # if delay and delay > 0:
        #     self.load_module(DelayModule(language=language, seconds=delay),
        #                      commit=(not any([bypass, anti_debug, dinvoke, syscalls, unhook, process])))
        # if unhook:
        #     self.load_module(module=UnhookModule(language=language, dinvoke=dinvoke),
        #                      commit=(not any([bypass, anti_debug, dinvoke, syscalls, process])))
        # if anti_debug:
        #     self.load_module(module=AntiDebugModule(language=language, dinvoke=dinvoke),
        #                      commit=(not any([bypass, dinvoke, syscalls, process])))
        # if bypass:
        #     self.load_module(
        #         module=AmsiModule(
        #             dinvoke=dinvoke,
        #             language=language,
        #         ),
        #         commit=not any([dinvoke, syscalls, process])
        #     )
        # if dinvoke and language == Language.CSHARP:
        #     self.load_module(module=DinvokeModule(),
        #                      commit=any([syscalls, process]))
        # if process:
        #     self.load_module(module=FindProcessModule(process=process, language=language),
        #                      commit=not syscalls)
        # if load_parameters_module:
        #     self.load_module(module=EvalArgsModule(language=language),
        #                      commit=not syscalls)
        # if syscalls and not dinvoke:
                #     self.load_module(
                # module=SyscallsModule(libraries=None, language=language),
                # commit=True)

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
            self.template.add_module(module)
        if commit:
            self.template.process_modules()

    def collect_sources(self):
        self.additional_sources = self.template.collect_sources()

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

    def clean(self):
        if os.path.isfile(self.outfile):
            os.unlink(self.outfile)
