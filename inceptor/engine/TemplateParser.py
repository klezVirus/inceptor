import argparse
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from engine.enums.Enums import LinkingMode
from enums.Architectures import Arch
from enums.Language import Language
from engine.factories.ModuleFactory import ModuleFactory
import yaml


class TemplateParser:

    def __init__(self):
        self.yaml = ""
        self.code = ""
        self.attributes = None
        self.language = None

    def __append_yaml(self, line):
        self.yaml += f"{line}\n"

    def __append_code(self, line):
        self.code += f"{line}\n"

    def __split_and_load(self, filename):
        with open(filename) as template:
            append = self.__append_yaml
            for line in template.readlines():
                if line.strip().startswith("---- CODE"):
                    append = self.__append_code
                    continue
                append(line)

    def __load_attributes(self):
        self.attributes = yaml.safe_load(self.yaml)

    def __detect_language(self, filename):
        self.language = Language.from_string(Path(filename).suffix)

    def parse(self, filename):
        self.__detect_language(filename)
        self.__split_and_load(filename)
        self.__load_attributes()

        modules = self.attributes.get("modules")
        dinvoke = False
        syscalls = False
        seconds = 0

        if modules:
            dinvoke = len([m for m in modules.keys() if m.lower() == "dinvoke"]) > 0
            syscalls = len([m for m in modules.keys() if m.lower() == "syscalls"]) > 0
            delay = modules.get("delay")

            if delay:
                seconds = modules.get("seconds") if modules.get("seconds") is not None else 30

        arch = self.attributes.get("arch")
        arch = Arch.from_string(arch if arch else "x64")
        print(f"Implant architecture: {arch}")
        language = Language.from_string(Path(filename).suffix[1:])
        kwargs = {
            "language": language,
            "seconds": seconds,
            "dinvoke": dinvoke,
            "syscalls": syscalls,
            "process": None,
            "pinject": False,
            "arch": arch,
            "shellcode": None,
            "linking_mode": LinkingMode.LIBRARY
        }

        for k, v in self.attributes.items():
            print(f"{k}: {v}")
            if k == "modules":
                for module_name in self.attributes.get(k):
                    m = ModuleFactory.from_name(module_name, **kwargs)
                    if m:
                        print(f"Created module object {m}!")


if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(description="Template Parser")
    parser.add_argument("filename", help="Template File")
    args = parser.parse_args()

    t_parser = TemplateParser()
    t_parser.parse(args.filename)
