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
from utils.utils import get_project_root, static_random_ascii_string, get_temporary_file


class AmsiModule(TemplateModule):

    def __init__(self, **kwargs):
        # Init variables
        libraries = None
        components = None
        ext = None
        library = None

        # We get the data we need to compute the template to use
        syscalls = kwargs["kwargs"]["syscalls"]
        dinvoke = kwargs["kwargs"]["dinvoke"]
        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        # Whatever the language is, we'll need a source code file
        source = get_temporary_file(ext=TemplateModule.get_extension_by_language(language=language))
        header = get_temporary_file(ext=".h")

        # And, if it's a "compiled" language, we'll need a library file, which might be a .lib or .dll
        if language == Language.CSHARP:
            ext = ".dll"
        elif language == Language.CPP:
            ext = ".lib"

        if ext:
            library = get_temporary_file(ext=ext)

        # We will need a namespace
        import_name = static_random_ascii_string(min_size=3, max_size=10)
        # We will need a class name
        class_name = static_random_ascii_string(min_size=3, max_size=10)
        # We will need a function
        function_name = static_random_ascii_string(min_size=3, max_size=10)
        # We will also need the bypass mode
        bypass_mode = Config().get('MISC', 'bypass_mode')

        # Now, we can fill the data for generate and build
        kwargs = {
            "language": language,
            "syscalls": syscalls,
            "dinvoke": dinvoke,
            "import": import_name,
            "class": class_name,
            "function": function_name,
            "library": library,
            "arch": arch,
            "source": source,
            "header": header
        }

        if language == Language.POWERSHELL:
            components = [
                BypassComponent(code=open(source).read()),
            ]
        elif language == Language.CSHARP:
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
            libraries = [library]
        else:
            raise ModuleNotCompatibleException()

        super().__init__(name="AmsiBypass", libraries=libraries, components=components, arch=arch)

    def generate(self, **kwargs):
        language = kwargs["kwargs"]["language"]
        _filter = Filter(exclude=["dinvoke", "powershell"])
        if kwargs["kwargs"]["dinvoke"]:
            _filter = Filter(include=["dinvoke"], exclude=["powershell"])
        template = TemplateFactory.get_module_template(self, language=language, _filter=_filter)
        if kwargs["kwargs"]["dinvoke"]:
            module = TemplateModule.from_name("dinvoke", kwargs=kwargs["kwargs"])
            template.add_module(module)

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
        compiler.default_dll_args(outfile=kwargs["kwargs"]["library"])
        compiler.set_libraries(template.libraries)
        compiler.compile([bypass_file])

