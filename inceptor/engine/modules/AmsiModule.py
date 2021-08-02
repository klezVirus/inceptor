import os
import sys
import tempfile
import traceback

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.BypassComponent import BypassComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.DinvokeModule import DinvokeModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root, static_random_ascii_string


class AmsiModule(TemplateModule):

    def __init__(self, **kwargs):

        dinvoke = kwargs["kwargs"]["dinvoke"]
        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        libraries = None
        components = None
        bypass_mode = Config().get('MISC', 'bypass_mode')

        if language == Language.POWERSHELL:
            path = str(Config().get_path("DIRECTORIES", "bypass"))
            allfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            chosen = TemplateFactory.choose_template(allfiles)
            code = open(chosen, "r").read()
            components = [
                BypassComponent(code=code),
            ]

        elif language == Language.CSHARP:
            import_name = static_random_ascii_string(min_size=3, max_size=10)
            class_name = static_random_ascii_string(min_size=3, max_size=10)
            function_name = static_random_ascii_string(min_size=3, max_size=10)

            dll = tempfile.NamedTemporaryFile(
                delete=True,
                dir=str(Config().get_path("DIRECTORIES", "WRITER")),
                suffix=".dll"
            ).name

            kwargs = {
                "language": language,
                "dinvoke": dinvoke,
                "import": import_name,
                "class": class_name,
                "function": function_name,
                "dll": dll
            }

            try:
                kwargs["template"] = self.generate(kwargs=kwargs)
                self.build(kwargs=kwargs)
            except:
                traceback.print_exc()
                print(f"[-] Exception building {self.__class__.__name__}")
                sys.exit(1)

            components = [
                BypassComponent(f"{import_name}.{class_name}.{function_name}(\"{bypass_mode}\");"),
                UsingComponent(f"{import_name}", language=language)
            ]
            libraries = [f"{dll}"]
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="AmsiBypass", libraries=libraries, components=components, arch=arch)

    def generate(self, **kwargs):
        _filter = Filter(exclude=["dinvoke", "powershell"])
        if kwargs["kwargs"]["dinvoke"]:
            _filter = Filter(include=["dinvoke"], exclude=["powershell"])
        template = TemplateFactory.from_path(
            path=str(Config().get_path("DIRECTORIES", "bypass").absolute()),
            _filter=_filter
        )
        if kwargs["kwargs"]["dinvoke"]:
            template.add_module(TemplateModule.from_name("dinvoke", kwargs=kwargs["kwargs"]))

        for k, v in zip(
            ["import", "class", "function"],
            ["####NAMESPACE####", "####CLASS####", "####FUNCTION####"]
        ):

            template.otf_replace(
                code=kwargs["kwargs"][k],
                placeholder=v
            )

        template.process_modules()
        return template

    def build(self, **kwargs):
        bypass_file = tempfile.NamedTemporaryFile(
            delete=False,
            dir=str(Config().get_path("DIRECTORIES", "WRITER")),
            suffix=".cs"
        ).name
        template = kwargs["kwargs"]["template"]
        with open(bypass_file, "w") as out:
            out.write(template.content)
        compiler = CscCompiler()
        compiler.default_dll_args(outfile=kwargs["kwargs"]["dll"])
        compiler.set_libraries(template.libraries)
        compiler.compile([bypass_file])

