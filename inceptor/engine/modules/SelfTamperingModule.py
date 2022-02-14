import os
import sys

from engine.Filter import Filter
from engine.TemplateFactory import TemplateFactory
from engine.component.BypassComponent import BypassComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DelayComponent import DelayComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.console import Console
from utils.utils import get_project_root, get_temporary_file, static_random_ascii_string


class DelayModule(TemplateModule):
    def generate(self, **kwargs):
        # We recollect all details from kwargs
        dinvoke = kwargs["dinvoke"]
        language = kwargs["language"]
        # source = kwargs["source"]
        # header = kwargs["header"]

        _filter = Filter(exclude=["dinvoke"])
        if dinvoke:
            _filter = Filter(include=["dinvoke"])
        template = TemplateFactory.get_module_template(self, language=language, _filter=_filter)

        if dinvoke:
            module = TemplateModule.from_name("dinvoke", kwargs=kwargs)
            template.add_module(module)

        for k, v in zip(
                ["import", "class", "function", "seconds", "microseconds"],
                ["####NAMESPACE####", "####CLASS####", "####FUNCTION####", "####SECONDS####", "####MICROSECONDS####"]
        ):
            template.otf_replace(
                code=kwargs[k],
                placeholder=v
            )
        template.process_modules()

        # with open(source, "w") as source_code:
        #     source_code.write(template.content)

        # with open(header, "w") as source_code:
        #     source_code.write(f"DWORD {kwargs['function']}();")

        return template

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):
        # Init variables
        libraries = None
        components = None
        ext = None
        library = None

        # Dereference kwargs
        kwargs = kwargs["kwargs"]

        # We get the data we need to compute the template to use
        syscalls = kwargs["syscalls"] if "syscalls" in kwargs.keys() else None
        dinvoke = kwargs["dinvoke"] if "dinvoke" in kwargs.keys() else None
        language = kwargs["language"]
        secs = kwargs["seconds"]
        arch = kwargs["arch"]

        # Let's generate the time as seconds and timeval struct
        useconds = str((secs - int(secs)) * 1000000)
        seconds = str(int(secs))

        if dinvoke or syscalls:
            Console.warn_line("[WARNING] Delay still doesn't support syscalls and manual mapping")

        if not seconds:
            Console.auto_line(f"[-] {self.__class__.__name__} requires (--delay)!")
            sys.exit(1)

        # THIS PART IS COMPLETELY USELESS RIGHT NOW

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

        # END OF THE USELESS PART

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
            "seconds": seconds,
            "microseconds": useconds,
        }

        # We can already update the libraries to contain the DLL/LIB (If any)
        libraries = []

        template = kwargs["template"] = self.generate(**kwargs)
        self.build(**kwargs)

        if language == Language.CPP:
            # Adding Ws2_32.lib to enable sleep by select
            # The select() api, however, is not working as expected (not sleeping)
            libraries = ["Ws2_32.lib"]
            components = [
                UsingComponent(code="<windows.h>", language=language),
                DelayComponent(code=template.content)
            ]
        elif language == Language.CSHARP:
            components = [
                DelayComponent(code=template.content)
            ]
        elif language == Language.POWERSHELL:
            components = [
                DelayComponent(code=template.content)
            ]
        else:
            raise ModuleNotCompatibleException()

        super().__init__(name="Delay", libraries=libraries, components=components)
