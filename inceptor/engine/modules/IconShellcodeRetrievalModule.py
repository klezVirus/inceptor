import os
import traceback
from binascii import unhexlify

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from compilers.CvtresCompiler import CvtresCompiler
from compilers.LibCompiler import LibCompiler
from compilers.RcCompiler import RcCompiler
from config.Config import Config
from engine.Filter import Filter
from engine.component.CodeComponent import CodeComponent
from engine.component.ShellcodeRetrievalComponent import ShellcodeRetrievalComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.IShellcodeRetrievalModule import IShellcodeRetrievalModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from engine.structures.Resource import Resource
from engine.structures.Ico import ICO
from engine.structures.ResourceSet import ResourceSet
from engine.structures.enums.ResourceType import ResourceType
from enums.Language import Language
from utils.utils import get_temporary_file, static_random_ascii_string


class IconShellcodeRetrievalModule(IShellcodeRetrievalModule):
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
        name = self.__class__.__name__

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
        # We need a resource set
        resources = ResourceSet()

        rc, __header = self.write_rc()

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
            "rc": rc,
            "resources": resources,
            "__header": __header
        }

        # We can already update the libraries to contain the DLL/LIB
        libraries = [library]

        # Setup shellcode length
        self.shellcode_length = len(shellcode)

        kwargs["template"], kwargs["args"] = self.generate(**kwargs)
        self.build(**kwargs)

        if language == Language.CPP:
            header = header.replace('\\', '\\\\')
            components = [
                UsingComponent(f"\"{header}\"", language=language),
                ShellcodeRetrievalComponent(code=f"{function_name}(&{kwargs['args']});",
                                            shellcode_length=self.shellcode_length),
            ]
        # This part will be enabled after the work on the ICON module is finalised
        elif language == Language.CSHARP:
            components = [
                UsingComponent(import_name, language=language),
                ShellcodeRetrievalComponent(code=rf"""{import_name}.{class_name}.{function_name}();""")
            ]
        # This part will be enabled after the work on the ICON module is finalised
        elif language == Language.POWERSHELL:
            raise ModuleNotCompatibleException()
            code = open(source).read()
            components = [
                CodeComponent(code=code),
                ShellcodeRetrievalComponent(code=rf"{function_name}")
            ]
        super().__init__(name=name, libraries=libraries, components=components, arch=arch, resources=resources)

    def generate(self, **kwargs):
        # We recollect all details from kwargs
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        source = kwargs["source"]
        header = kwargs["header"]
        kwargs["__header"] = f'#include "{kwargs["__header"]}"'
        shellcode = kwargs["shellcode"]

        # We need to modify the shellcode based on the retrieval method
        kwargs["return"], args, kwargs["shellcode"] = self.craft(shellcode, language)

        # Format arguments in a nice way
        # Transformed into (char*, int, ...)
        kwargs["args_h"] = ", ".join([f"{args[i].split(' ')[0]}" for i in range(len(args))])
        # Transformed into (arg0, arg1, ...)
        kwargs["args_f"] = ", ".join([f"{args[i].split(' ')[1]}" for i in range(len(args))])
        # Transformed into (char* arg0, int arg1, ...)
        kwargs["args"] = ", ".join([f"{args[i]}" for i in range(len(args))])

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
                [
                     "import",
                     "class",
                     "function",
                     "return",
                     "args",
                     "shellcode",
                     "__header"
                 ],
                [
                    "####NAMESPACE####",
                    "####CLASS####",
                    "####FUNCTION####",
                    "####RET####",
                    "####ARGS####",
                    "####SHELLCODE####",
                    "//####USING####"
                ]
        ):
            template.otf_replace(
                code=kwargs[k],
                placeholder=v
            )
        # Perform shellcode length replacement
        template.otf_replace(
            code=str(len(shellcode)),
            placeholder="####SHELLCODE_LENGTH####"
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
            # Replace Dereferenced Arguments

        # Finally generate final module
        template.process_modules()

        # Write into source file for compilation
        with open(source, "w") as source_code:
            source_code.write(template.content)

        # Write an header file for compilation if needed
        with open(header, "w") as source_code:
            source_code.write(rf"""{kwargs['return']} {kwargs['function']}({kwargs['args_h']});""")

        return template, kwargs['args_f']

    def build(self, **kwargs):
        rc = kwargs["rc"]
        arch = kwargs["arch"]
        source = kwargs["source"]
        language = kwargs["language"]
        library = kwargs["library"]
        template = kwargs["template"]
        resources = kwargs["resources"]
        if language == Language.POWERSHELL:
            return

        object_file = None
        if language == Language.CSHARP:
            compiler = CscCompiler(arch=arch.value)
            compiler.default_dll_args(outfile=library)
            resources.append(Resource(resource_type=ResourceType.ICO, path=Config().get_temp_folder().joinpath("favicon_ico")))
        else:
            res = get_temporary_file(".res")
            obj = get_temporary_file(".o")
            rc_compiler = RcCompiler(arch=arch.value)
            rc_compiler.default_args(outfile=res)
            rc_compiler.add_include_directory(str(Config().get_temp_folder()))
            rc_compiler.compile([rc])
            if not (res and os.path.isfile(res)):
                raise FileNotFoundError(f"File {res} not compiled")
            cvtres_compiler = CvtresCompiler(arch=arch.value)
            cvtres_compiler.default_args(outfile=obj)
            cvtres_compiler.compile([res])

            resources.append(Resource(resource_type=ResourceType.ICO, path=obj))

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

    def craft(self, shellcode, language) -> (str, list, str):
        data = shellcode
        if isinstance(shellcode, str):
            data = unhexlify(shellcode)
        icon_file = Config().get_temp_folder().joinpath("favicon_ico")
        if language == Language.POWERSHELL:
            with open(icon_file, "wb") as icon:
                icon.write(data)
            raise ModuleNotCompatibleException
        if language == Language.CSHARP:
            ico = ICO(payload=shellcode)
            ico.save(icon_file)
            return "byte[]", [], ""
        elif language == Language.CPP:
            ico = ICO(payload=shellcode)
            ico.save(icon_file)
            return "unsigned char*", ["int* length"], ""

    def write_rc(self):
        # Write resource.h
        header = get_temporary_file(ext=".h")
        # I guess we can replace FAVICON_ICO with a random
        # Also the 100 could be replaced with a random number
        # Except for 32512 - 32518, which are well known values
        # Are there others?
        with open(header, "w") as source:
            source.write("#define FAVICON_ICO 100\n")
        header = header.replace("\\", "\\\\")
        rc = get_temporary_file(ext=".rc")
        with open(rc, "w") as source:
            source.write(rf"""#include "{header}"
FAVICON_ICO RCDATA favicon_ico
            """)
        return rc, header
