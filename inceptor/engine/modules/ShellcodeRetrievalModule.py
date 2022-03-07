import os
import traceback
from abc import ABC, abstractmethod

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.LibCompiler import LibCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.component.CodeComponent import CodeComponent
from engine.component.ShellcodeRetrievalComponent import ShellcodeRetrievalComponent
from engine.component.UsingComponent import UsingComponent
from engine.enums.Enums import LinkingMode
from engine.modules.AdditionalSourceModule import AdditionalSourceModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.utils import get_temporary_file, static_random_ascii_string


class IShellCodeRetrievalModule:
    pass


class ShellcodeRetrievalModule(TemplateModule, ABC, IShellCodeRetrievalModule):
    def __init__(self, **kwargs):
        # Init variables
        libraries = []
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
        shellcode = kwargs["shellcode"]
        name = kwargs["name"] if "name" in kwargs.keys() else "ShellcodeRetrieval"
        linking_mode = kwargs["linking_mode"] if "linking_mode" in kwargs.keys() else LinkingMode.LIBRARY

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
            "shellcode": shellcode,
            "linking_mode": linking_mode
        }

        if linking_mode == LinkingMode.LIBRARY:
            # We can already update the libraries to contain the DLL/LIB
            libraries = [library]

        # Setup shellcode length
        self.shellcode_length = len(shellcode)

        kwargs["template"], kwargs["args"] = self.generate(**kwargs)

        if linking_mode == LinkingMode.LIBRARY:
            self.build(**kwargs)

        if language == Language.CPP:
            header = header.replace('\\', '\\\\')
            components = [
                UsingComponent(f"\"{header}\"", language=language),
                ShellcodeRetrievalComponent(code=f"{function_name}({kwargs['args']});", shellcode_length=self.shellcode_length),
            ]
        elif language == Language.CSHARP:
            components = [
                UsingComponent(import_name, language=language),
                ShellcodeRetrievalComponent(code=rf"""{import_name}.{class_name}.{function_name}();""")
            ]
        elif language == Language.POWERSHELL:
            code = open(source).read()
            components = [
                CodeComponent(code=code),
                ShellcodeRetrievalComponent(code=rf"{function_name}")
            ]
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name=name, libraries=libraries, components=components, arch=arch)
        if linking_mode == LinkingMode.SOURCE:
            self.additional_modules.append(AdditionalSourceModule(content=None, path=source))

    def generate(self, **kwargs):
        # We recollect all details from kwargs
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        source = kwargs["source"]
        header = kwargs["header"]
        shellcode = kwargs["shellcode"]

        # We need to modify the shellcode based on the retrieval method
        kwargs["return"], args, kwargs["shellcode"] = self.craft(shellcode, language)

        # Format arguments in a nice way
        # Transformed into (char*, int, ...)
        kwargs["args_h"] = ", ".join([f"{args[i]}" for i in range(len(args))])
        # Transformed into (arg0, arg1, ...)
        kwargs["args_f"] = ", ".join([f"arg{i}" for i in range(len(args))])
        # Transformed into (char* arg0, int arg1, ...)
        kwargs["args"] = ", ".join([f"{args[i]} arg{i}" for i in range(len(args))])

        # Create a filter to skim the module templates
        _filter = Filter(exclude=["dinvoke"])
        if dinvoke:
            _filter = Filter(include=["dinvoke"])
        # Bypass filter for ShellcodeRetrieval
        is_srm = any([s.filename.find("ShellcodeRetrievalModule") > -1 for s in traceback.extract_stack()])
        if is_srm:
            _filter = None

        # Get the module template among the ones matching the filter
        from engine.factories.TemplateFactory import TemplateFactory
        template = TemplateFactory.get_srm_template(self, language=language, _filter=_filter)

        # Add D/Invoke module before compilation if needed
        if dinvoke:
            module = TemplateModule.from_name("dinvoke", kwargs=kwargs)
            template.add_module(module)

        # Perform random replacements
        for k, v in zip(
                ["import", "class", "function", "return", "args", "shellcode"],
                ["####NAMESPACE####", "####CLASS####", "####FUNCTION####", "####RET####", "####ARGS####", "####SHELLCODE####"]
        ):
            template.otf_replace(
                code=kwargs[k],
                placeholder=v
            )
        # Perform ARGV replacement
        for i in range(len(args)):
            # Replace Arguments "in-use"
            template.otf_replace(
                code=f"arg{i}",
                placeholder=f"####ARG{i}####"
            )
            # Replace Arguments at "declaration"
            template.otf_replace(
                code=f"{args[i]} arg{i}",
                placeholder=f"####INIT_ARG{i}####"
            )

        # Finally generate final module
        template.process_modules()

        # Write into source file for compilation
        with open(source, "w") as source_code:
            source_code.write(template.content)

        # Write an header file for compilation if needed
        with open(header, "w") as source_code:
            source_code.write(rf"""
            {kwargs['return']} {kwargs['function']}({kwargs['args_h']});
            """)

        return template, kwargs['args_f']

    def build(self, **kwargs):

        source = kwargs["source"]
        language = kwargs["language"]
        library = kwargs["library"]
        template = kwargs["template"]
        arch = kwargs["arch"]

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

    @abstractmethod
    def craft(self, shellcode, language):
        pass
