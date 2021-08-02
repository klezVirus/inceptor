import re

from config.Config import Config
from converters.Transformer import Transformer
from utils.console import Console
from utils.utils import *


class Donut(Transformer):
    def __init__(self):
        self.donut = str(Config().get_path("DIRECTORIES", "libs").joinpath("donut.exe"))
        self.args = "-e3 -a2 -b1 "
        super().__init__()
        self.filetype = "exe"
        self.output_path = Config().get_path("DIRECTORIES", "writer")
        self.output_file_ext = "bin"
        self.debug = Config().get_boolean("DEBUG", "LOADERS")

    def transform(self, target):
        if not os.path.isfile(target):
            print(f"[-] File not found: {target}")
            sys.exit(1)
        filename = os.path.basename(os.path.splitext(target)[0])
        target = Path(target).absolute()
        converted = str(self.output_path.joinpath(f"{filename}.{self.output_file_ext}"))
        try:
            cmd = f'"{self.donut}" {self.args} -f1 "{target}" -o "{converted}"'
            if self.debug:
                Console.auto_line(f"  [>] Donut cmdline: {cmd}")
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            output = e.output
            Console.fail_line(output.decode())
        mark = re.compile(r'\s*Shellcode\s*:')
        if not re.search(mark, output.decode()):
            Console.auto_line(f"[-] Failed to convert {target}")
            sys.exit(1)
        if not os.path.isfile(converted):
            Console.auto_line(f"[-] Failed to locate converted file: {converted}")
            sys.exit(1)
        with open(converted, "rb") as donut:
            return donut.read()

    def add_parameters(self, params):
        if params:
            self.args += f'-p "{params}"'

    def set_architecture(self, arch="x64", tool_arch=None):
        if arch == "x86" or tool_arch == "x86":
            self.args += "-a1 "
        if arch == "x64" or tool_arch == "x64":
            self.args += "-a2 "
        elif arch == "anycpu" and not tool_arch:
            self.args += "-a3 "
