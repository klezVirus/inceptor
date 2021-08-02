import os
import subprocess

from config.Config import Config
from obfuscators.Obfuscator import Obfuscator, MissingArgumentException
from utils.utils import get_project_root


class LoGIC_NET(Obfuscator):
    def __init__(self, **kwargs):
        super().__init__(sep=" ", path=None, args={})

        self.name = self.name.replace('_', '.')

        self.path = os.path.join(
            get_project_root(),
            Config().get("OBFUSCATORS", "dotnet"),
            self.name,
            f"{self.name}.exe")
        self.args = {}
        dinvoke = "dinvoke" in kwargs['kwargs'].keys()
        if "filename" not in kwargs['kwargs'].keys():
            raise MissingArgumentException("A file to obfuscate is required")

        filename = f"\"{kwargs['kwargs']['filename']}\""
        self.outfile = f"{kwargs['kwargs']['filename']}.obfuscated"
        self.args[filename] = None
        self.args[f'"{self.outfile}"'] = None

        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator utility file")

        if not os.path.isfile(kwargs['kwargs']["filename"]):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator target file")

    def obfuscate(self):
        try:
            args = ""
            for k in self.args.keys():
                args += f" {k}{self.sep}{self.args[k]}" if self.args[k] is not None else f" {k}"
            cmd = f"\"{self.path}\" {args}"
            if self.debug:
                print(cmd)
            output = subprocess.check_output(cmd).decode().strip()
            if self.debug:
                print(output)
            if os.path.isfile(self.outfile):
                print(f"  [>] Obfuscated filename: {self.outfile}")
        except subprocess.CalledProcessError:
            print(f"[-] Failed to obfuscate payload with {self.name}")
        return self.outfile
