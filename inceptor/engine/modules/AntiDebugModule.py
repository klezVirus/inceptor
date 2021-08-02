import os
import sys
import tempfile
import traceback

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.LibCompiler import LibCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.DinvokeModule import DinvokeModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root, static_random_ascii_string


class AntiDebugModule(TemplateModule):
    def __init__(self, **kwargs):
        libraries = []

        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        import_name = static_random_ascii_string(min_size=3, max_size=10)
        class_name = static_random_ascii_string(min_size=3, max_size=10)
        function_name = static_random_ascii_string(min_size=3, max_size=10)

        kwargs = {
            "dinvoke": False,
            "import": import_name,
            "class": class_name,
            "function": function_name,
        }

        if language == Language.CSHARP:
            library = tempfile.NamedTemporaryFile(
                delete=True,
                dir=str(Config().get_path("DIRECTORIES", "WRITER")),
                suffix=".dll"
            ).name

            components = [
                AntiDebugComponent(f"{import_name}.{class_name}.{function_name}();"),
                UsingComponent(import_name, language=language)
            ]
        elif language == Language.CPP:
            libraries.append("dbghelp.lib")
            library = tempfile.NamedTemporaryFile(
                delete=True,
                dir=str(Config().get_path("DIRECTORIES", "WRITER")),
                suffix=".lib"
            ).name

            components = [
                CodeComponent(rf"""
                extern bool {function_name}(void);
                """),
                AntiDebugComponent(rf"""
                        if ({function_name}()){{
                            exit(-1);
                        }}
                    """)
            ]
        else:
            raise ModuleNotCompatibleException()
        try:
            kwargs["dll"] = library
            kwargs["language"] = language
            kwargs["template"] = self.generate(kwargs=kwargs)
            self.build(kwargs=kwargs)
        except:
            traceback.print_exc()
            print(f"[-] Exception building {self.__class__.__name__}")
            sys.exit(1)

        libraries.append(library)
        super().__init__(name="AntiDebug", libraries=libraries, components=components, arch=arch)

    def generate(self, **kwargs):
        if "language" not in kwargs["kwargs"].keys():
            raise NotImplementedError(f"Module {self.__class__.__name__} needs a language to build")
        language = kwargs["kwargs"]["language"]

        if language == language.CSHARP:
            _filter = Filter(exclude=["dinvoke"])
            if kwargs["kwargs"]["dinvoke"]:
                _filter = Filter(include=["dinvoke"])

            template = TemplateFactory.from_path(
                path=os.path.join(
                    get_project_root(),
                    Config().get("DIRECTORIES", "dotnet"),
                    Config().get("DIRECTORIES", "antidebug")),
                _filter=_filter
            )
        else:
            template = TemplateFactory.from_path(
                path=os.path.join(
                    get_project_root(),
                    Config().get("DIRECTORIES", "native"),
                    Config().get("DIRECTORIES", "antidebug"))
            )

        for k, v in zip(
                ["import", "class", "function"],
                ["####NAMESPACE####", "####CLASS####", "####FUNCTION####"]
        ):
            template.otf_replace(
                code=kwargs["kwargs"][k],
                placeholder=v
            )

        if kwargs["kwargs"]["dinvoke"] and language == language.CSHARP:
            template.add_module(DinvokeModule(language=Language.CSHARP))

        template.process_modules()
        return template

    def build(self, **kwargs):
        if "language" not in kwargs["kwargs"].keys():
            raise NotImplementedError(f"Module {self.__class__.__name__} needs a language to build")
        language = kwargs["kwargs"]["language"]
        nodebug_file = tempfile.NamedTemporaryFile(
                delete=False,
                dir=str(Config().get_path("DIRECTORIES", "WRITER"))
            ).name
        if language == Language.CSHARP:
            nodebug_file += ".cs"
        else:
            nodebug_file += ".cpp"

        template = kwargs["kwargs"]["template"]
        with open(nodebug_file, "w") as out:
            out.write(template.content)
        if language == Language.CSHARP:
            compiler = CscCompiler()
            compiler.default_dll_args(outfile=kwargs["kwargs"]["dll"])
            compiler.set_libraries(template.libraries)
            compiler.compile([nodebug_file])
        else:
            object_file = os.path.splitext(kwargs["kwargs"]["dll"])[0] + ".obj"
            compiler = ClCompiler()
            compiler.default_obj_args(outfile=object_file)
            compiler.set_libraries(["dbghelp.lib"])
            compiler.compile([nodebug_file])
            compiler = LibCompiler()
            compiler.default_args(outfile=kwargs["kwargs"]["dll"])
            compiler.compile([object_file])

