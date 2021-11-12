import os
import sys

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.LibCompiler import LibCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.CodeComponent import CodeComponent
from engine.component.FindProcessComponent import FindProcessComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from engine.component.BypassComponent import BypassComponent
from engine.component.DelayComponent import DelayComponent
from utils.console import Console
from utils.utils import get_project_root, static_random_ascii_string, get_temporary_file


class FindProcessModule(TemplateModule):
    def generate(self, **kwargs):
        # We recollect all details from kwargs
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        source = kwargs["source"]
        header = kwargs["header"]

        _filter = Filter(exclude=["dinvoke"])
        if dinvoke:
            _filter = Filter(include=["dinvoke"])
        template = TemplateFactory.get_module_template(self, language=language, _filter=_filter)

        if dinvoke:
            module = TemplateModule.from_name("dinvoke", kwargs=kwargs)
            template.add_module(module)

        for k, v in zip(
                ["import", "class", "function", "process"],
                ["####NAMESPACE####", "####CLASS####", "####FUNCTION####", "####PROCESS####"]
        ):
            template.otf_replace(
                code=kwargs[k],
                placeholder=v
            )
        template.process_modules()

        with open(source, "w") as source_code:
            source_code.write(template.content)

        with open(header, "w") as source_code:
            source_code.write(f"DWORD {kwargs['function']}();")

        return template

    def build(self, **kwargs):
        source = kwargs["source"]
        language = kwargs["language"]
        library = kwargs["library"]
        template = kwargs["template"]
        arch = kwargs["arch"]

        # Let's put an early return on POWERSHELL
        if language == Language.POWERSHELL:
            return

        object_file = None
        if language == Language.CSHARP:
            compiler = CscCompiler(arch=arch.value)
            compiler.default_dll_args(outfile=library)
        else:
            compiler = ClCompiler(arch=arch.value)
            object_file = os.path.splitext(library)[0] + ".obj"
            compiler.default_obj_args(outfile=object_file)
            compiler.add_include_directory(str(Config().get_path("DIRECTORIES", "WRITER")))
        # compiler.set_libraries(template.libraries)
        compiler.compile([source])

        if object_file and os.path.isfile(object_file):
            libc = LibCompiler(arch=arch.value)
            libc.default_args(outfile=library)
            libc.compile([object_file])

    def __init__(self, **kwargs):
        # Init variables
        libraries = None
        components = None
        ext = None
        library = None

        # Dereference kwargs
        while "kwargs" in kwargs.keys():
            kwargs = kwargs["kwargs"]

        # We get the data we need to compute the template to use
        syscalls = kwargs["syscalls"] if "syscalls" in kwargs.keys() else None
        dinvoke = kwargs["dinvoke"] if "dinvoke" in kwargs.keys() else None
        language = kwargs["language"]
        process = kwargs["process"]
        pinject = kwargs["pinject"]

        # Let's craft the process array into a C/C#/PS array
        if language == Language.CPP:
            process = [f'L"{p}.exe"' for p in process]
        else:
            process = [f'"{p}"' for p in process]

        process = ",".join(process)

        if dinvoke or syscalls:
            Console.warn_line("[WARNING] Find process still doesn't support syscalls and manual mapping")

        if not pinject:
            Console.auto_line(f"[-] {self.__class__.__name__} requires (-P|--pinject)!")
            sys.exit(1)
        if not process:
            Console.auto_line(f"[-] {self.__class__.__name__} requires (-PN|--process)!")
            sys.exit(1)

        arch = kwargs["arch"]

        # Now let's warn everyone that this module still doesn't have a dinvoke/syscall version
        if dinvoke or syscalls:
            Console.warn_line("[#] This module has still no support for D/Invoke or Syscalls")

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
            "header": header,
            "process": process
        }

        # We can already update the libraries to contain the DLL/LIB
        libraries = [library]

        kwargs["template"] = self.generate(**kwargs)
        self.build(**kwargs)

        if language == Language.CPP:
            header = header.replace('\\', '\\\\')
            components = [
                UsingComponent(f"\"{header}\"", language=language),
                FindProcessComponent(code=f"pid = {function_name}();")
            ]
        elif language == Language.CSHARP:
            components = [
                UsingComponent(import_name, language=language),
                FindProcessComponent(code=rf"""
                        pid = {import_name}.{class_name}.{function_name}();
                        """)
            ]
        elif language == Language.POWERSHELL:
            components = [
                CodeComponent(code=open(source).read()),
                FindProcessComponent(code=rf"""
                        $targetpid = {function_name}
                        """)
            ]
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="FindProcess", libraries=libraries, components=components)
