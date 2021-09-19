import re

from config.Config import Config
from converters.TransfomerExceptions import ConversionError
from converters.Transformer import Transformer
from utils.console import Console
from utils.utils import *


class ArchitectureMismatch(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Donut(Transformer):
    def __init__(self):
        self.donut = str(Config().get_path("DIRECTORIES", "libs").joinpath("donut.exe"))
        self.args = "-e3 -b1 "
        self.arch = Arch.x64
        super().__init__()
        self.filetype = "exe"
        self.output_path = Config().get_path("DIRECTORIES", "writer")
        self.output_file_ext = "bin"

    def transform(self, target):
        if not os.path.isfile(target):
            raise FileNotFoundError(f"[-] File not found: {target}")
        filename = os.path.basename(os.path.splitext(target)[0])
        target = Path(target).absolute()
        if detect_arch(target) != self.arch:
            raise ArchitectureMismatch(
                f"The target binary is {detect_arch(target).value}, while donut is running as {self.arch.value}"
            )
        converted = str(self.output_path.joinpath(f"{filename}.{self.output_file_ext}"))
        try:
            cmd = f'"{self.donut}" {self.architecture()} {self.args} -f1 "{target}" -o "{converted}"'
            if self.debug:
                Console.auto_line(f"  [>] Donut cmdline: {cmd}")
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if self.debug:
                Console.auto_line(f"  [>] Donut output:\n {output.decode()}")
        except subprocess.CalledProcessError as e:
            output = e.output
            Console.fail_line(output.decode())
            sys.exit(1)
        mark = re.compile(r'\s*Shellcode\s*:')
        if not re.search(mark, output.decode()):
            raise ConversionError(f"Failed to convert {target}")
        if not os.path.isfile(converted):
            raise FileNotFoundError(f"Failed to locate converted file: {converted}")
        with open(converted, "rb") as donut:
            return donut.read()

    def add_parameters(self, params):
        if params:
            self.args += f'-p "{params}"'

    def architecture(self):
        if self.arch == Arch.x86:
            return "-a1 "
        elif self.arch == Arch.x64:
            return "-a2 "
        elif self.arch == Arch.Any:
            return "-a3 "

    def set_architecture(self, arch="x64", tool_arch=None):
        if arch == "x86" or tool_arch == "x86":
            self.arch = Arch.x86
        elif arch == "x64" or tool_arch == "x64":
            self.arch = Arch.x64
        elif arch == "anycpu" and not tool_arch:
            self.arch = Arch.Any

    def set_additional_arguments(self, **kwargs):
        if "classname" in kwargs['kwargs'].keys():
            classname = kwargs['kwargs']['classname']
            if classname and classname != "":
                self.args = f"-c {classname}"
        if "function" in kwargs['kwargs'].keys():
            function = kwargs['kwargs']['function']
            if function and function != "":
                self.args += f"-m {function}"
