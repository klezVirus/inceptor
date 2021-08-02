import base64
import os
import re
import subprocess
import sys

from config.Config import Config
from converters.Transformer import Transformer
from utils.console import Console
from utils.utils import *


class Pe2sh(Transformer):
    def __init__(self):
        self.pe2sh = str(Config().get_path("DIRECTORIES", "libs").joinpath("pe2sh.exe"))
        self.output_path = Config().get_path("DIRECTORIES", "writer")
        super().__init__()
        self.filetype = "exe"

    def transform(self, target):
        if not os.path.isfile(target):
            print(f"[-] File not found: {target}")
            sys.exit(1)
        target_file_name, target_file_ext = os.path.splitext(target)
        outfile = str(self.output_path.joinpath(os.path.basename(target_file_name)))
        try:
            output = subprocess.check_output(f'"{self.pe2sh}" "{target}" "{outfile}.shc{target_file_ext}"')
        except subprocess.CalledProcessError as e:
            output = e.output
            Console.fail_line(output.decode())
        if re.search(rb"\[WARNING\]", output):
            Console.warn_line("  " + re.search(rb"\[WARNING\].*", output)[0].decode().strip())
            Console.warn_line(f"  [WARNING] {target.split(chr(92))[-1]} may not work in .NET")
        if not re.search(rb"\[\+\]\sSaved\sas\:", output):
            Console.auto_line(f"[-] Failed to convert {target}")
            sys.exit(1)
        converted = f"{target_file_name}.shc{target_file_ext}"
        if not os.path.isfile(converted):
            Console.auto_line(f"[-] Failed to locate converted file: {converted}")
            sys.exit(1)
        return bin2hex4pe2sh(converted)
