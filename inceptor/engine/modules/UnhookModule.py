import os

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.LibCompiler import LibCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root, get_temporary_file, static_random_ascii_string


class UnhookModule(TemplateModule):
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
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        arch = kwargs["arch"]

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
        # We will also need an alternate data stream name
        ads = static_random_ascii_string(min_size=3, max_size=10)

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
            "ads": ads
        }

        # We can already update the libraries to contain the DLL/LIB
        libraries = [library]

        kwargs["template"] = self.generate(**kwargs)
        self.build(**kwargs)

        if language == Language.CPP:
            header = header.replace('\\', '\\\\')
            components = [
                UsingComponent(f"\"{header}\"", language=language),
                UnhookComponent(code=f"{function_name}();")
            ]
        elif language == Language.CSHARP:
            components = [
                UsingComponent(import_name, language=language),
                UnhookComponent(code=rf"""
                        {import_name}.{class_name}.{function_name}();
                        """)
            ]
        elif language == Language.POWERSHELL:
            components = [
                CodeComponent(code=open(source).read()),
                UnhookComponent(code=r"""
                        Invoke-IceCreamPopper
                        """)
            ]
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="Unhook", libraries=libraries, components=components, arch=arch)

    def generate(self, **kwargs):
        # We recollect all details from kwargs
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        source = kwargs["source"]
        header = kwargs["header"]

        # Create a filter to skim the module templates
        _filter = Filter(exclude=["dinvoke"])
        if dinvoke:
            _filter = Filter(include=["dinvoke"])

        # Get the module template among the ones matching the filter
        template = TemplateFactory.get_module_template(self, language=language, _filter=_filter)

        # Add D/Invoke module before compilation if needed
        if dinvoke:
            module = TemplateModule.from_name("dinvoke", kwargs=kwargs)
            template.add_module(module)

        # Perform random replacements
        for k, v in zip(
                ["import", "class", "function"],
                ["####NAMESPACE####", "####CLASS####", "####FUNCTION####"]
        ):
            template.otf_replace(
                code=kwargs[k],
                placeholder=v
            )
        # Finally generate final module
        template.process_modules()

        # Write into source file for compilation
        with open(source, "w") as source_code:
            source_code.write(template.content)

        # Write an header file for compilation if needed
        with open(header, "w") as source_code:
            source_code.write(f"int {kwargs['function']}();")

        return template

    def build(self, **kwargs):

        source = kwargs["source"]
        language = kwargs["language"]
        library = kwargs["library"]
        template = kwargs["template"]
        arch = kwargs["arch"]

        object_file = None
        if language == Language.CSHARP:
            compiler = CscCompiler(arch=arch.value)
            compiler.default_dll_args(outfile=library)
        else:
            compiler = ClCompiler(arch=arch.value)
            object_file = os.path.splitext(library)[0] + ".obj"
            compiler.default_obj_args(outfile=object_file)
            compiler.add_include_directory(str(Config().get_path("DIRECTORIES", "WRITER")))
            # The Unhooking module requires dbghelp.lib
            compiler.set_libraries(["dbghelp.lib"])
        # compiler.set_libraries(template.libraries)
        compiler.compile([source])

        if object_file and os.path.isfile(object_file):
            libc = LibCompiler(arch=arch.value)
            libc.default_args(outfile=library)
            libc.compile([object_file])
