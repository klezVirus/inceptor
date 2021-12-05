import os
import sys
import re
import glob
import traceback

from config.Config import Config
from converters.Donut import Donut
from converters.Loader import Loader
from converters.Pe2Shellcode import Pe2sh
from engine.Filter import Filter
from engine.Template import Template
from enums.Language import Language
from utils.console import Console
from utils.utils import get_project_root, isDotNet


class TemplateFactory:

    @staticmethod
    def get_module_template(obj, language, _filter: Filter = None):
        directory = obj.__class__.__name__.lower().replace("module", "")
        path = Config().get_path("DIRECTORIES", "templates").joinpath(language.name.lower()).joinpath("modules").joinpath(directory)
        template = TemplateFactory.from_path(path, language=language, _filter=None, is_module=True)
        if not template:
            return FileNotFoundError(f"{path} not found")
        return template

    @staticmethod
    def get_srm_template(obj, language, _filter: Filter = None):
        directory = obj.__class__.__name__.lower().replace("module", "")
        path = Config().get_path("DIRECTORIES", "templates").joinpath(language.name.lower()).joinpath("modules").joinpath("shellcoderetrieval").joinpath(directory)
        template = TemplateFactory.from_path(path, language=language, _filter=_filter, is_module=True)
        if not template:
            return FileNotFoundError(f"{path} not found")
        return template

    @staticmethod
    def from_path(path, language=Language.CSHARP, _filter: Filter = None, is_module=False):
        allfiles = []
        temp = ""
        if Config().get_boolean("DEBUG", "WRITER"):
            Console.warn_line(f"[DEBUG] Loading from: {path}")
            if _filter:
                Console.warn_line(f"[DEBUG] With filter:")
                Console.warn_line(f"  [>] Include: {_filter.include}")
                Console.warn_line(f"  [>] Exclude: {_filter.exclude}")
        if os.path.isfile(path):
            return Template(path=path, language=language)
        elif os.path.isdir(path):
            allfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if _filter:
            allfiles = [f for f in allfiles if _filter.match(f)]
        if len(allfiles) > 1:
            temp = TemplateFactory.choose_template(allfiles)
        elif len(allfiles) == 1:
            temp = allfiles[0]
        else:
            Console.fail_line("[-] Template not found")
            exit(1)

        path = os.path.join(path, temp)
        if not os.path.isfile(path=path):
            Console.auto_line("  [-] Error with template")
            sys.exit(1)
        return Template(path=path, language=language, ignore_errors=is_module)

    @staticmethod
    def from_converter(file=None,
                       converter=None,
                       language=Language.CSHARP,
                       dinvoke=False,
                       syscalls=False,
                       pinject=False,
                       _filter: Filter = None):
        base_directory, template, template_file = None, None, None
        artifact_type = None
        if file:
            filename, ext = os.path.splitext(file)
            artifact_type = ext.replace(".", "")

        if language == Language.CPP:
            base_directory = Config().get("DIRECTORIES", "NATIVE")
        elif language == Language.POWERSHELL:
            base_directory = Config().get("DIRECTORIES", "POWERSHELL")
        elif language == language.CSHARP:
            base_directory = Config().get("DIRECTORIES", "DOTNET")
        else:
            Console.auto_line(f"[-] {language} Not supported")
            sys.exit(1)
        base_directory = os.path.join(get_project_root(), base_directory,
                                      "process_injection" if pinject else "code_execution")
        allfiles = [f for f in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, f))]
        # print(allfiles)
        if not _filter:
            _filter = Filter()
        _filter.imode = "and"
        if artifact_type in ["exe", "dll"] and not isDotNet(file) and (
                isinstance(converter, Loader) or isinstance(converter, Pe2sh)):
            _filter.exclude.append("assembly_load")
            _filter.include.append("pe_load")
        elif artifact_type in ["exe", "dll"] and not isDotNet(file) and isinstance(converter, Donut):
            _filter.exclude.append("assembly_load")
            _filter.exclude.append("pe_load")
        else:
            _filter.exclude.append("pe_load")
        if dinvoke:
            _filter.include.append("dinvoke")
        else:
            _filter.exclude.append("dinvoke")
        if syscalls:
            _filter.include.append("syscalls")
        else:
            _filter.exclude.append("syscalls")

        allfiles = [f for f in allfiles if _filter.match(f)]

        if len(allfiles) == 0:
            Console.auto_line("[-] No template found with given criteria")
            sys.exit(1)
        elif len(allfiles) > 1:
            temp = TemplateFactory.choose_template(allfiles)
        else:
            temp = allfiles[0]

        path = os.path.join(base_directory, temp)

        if not os.path.isfile(path=path):
            Console.auto_line(
                f"[#] Template file: {template_file} does not support "
                f"{'process injection' if pinject else 'code execution'}"
            )
            sys.exit(1)
        t = Template(path=path, language=language)
        return t

    @staticmethod
    def choose_template(templates: list):
        try:
            Console.auto_line("[*] Multiple compatible templates identified, choose one:")
            choice = -1
            for n, t in enumerate(templates, start=0):
                Console.auto_line(f"  {n}: {t}")
            while not 0 <= choice <= len(templates) - 1:
                try:
                    choice = int(input("  $> "))
                except ValueError:
                    continue
            return templates[choice]
        except KeyboardInterrupt:
            Console.auto_line("[-] Aborting")
            sys.exit(1)
