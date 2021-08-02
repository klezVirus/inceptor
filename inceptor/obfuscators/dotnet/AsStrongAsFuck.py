import os
import subprocess

from config.Config import Config
from obfuscators.Obfuscator import Obfuscator, MissingArgumentException
from utils.utils import get_project_root


class AsStrongAsFuck(Obfuscator):
    def __init__(self, **kwargs):
        super().__init__(sep=" ", path=None, args={})

        self.path = os.path.join(get_project_root(), Config().get("OBFUSCATORS", "dotnet"), self.name, f"{self.name}.exe")
        self.args = {}
        dinvoke = "dinvoke" in kwargs['kwargs'].keys()
        if "filename" not in kwargs['kwargs'].keys():
            raise MissingArgumentException("A file to obfuscate is required")

        if dinvoke:
            self.args["-o"] = "25789"
        else:
            self.args["-o"] = "235789"
        self.args["-f"] = f"\"{kwargs['kwargs']['filename']}\""

        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator utility file")

        if not os.path.isfile(kwargs['kwargs']["filename"]):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator target file")

    def obfuscate(self):
        out_filename = None
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
            for line in output.split("\n"):
                if line.find("Saving as") > - 1:
                    out_filename = os.path.join(get_project_root(), " ".join(line.split(" ")[2:]).strip())
                    print(f"  [>] Obfuscated filename: {out_filename}")
        except subprocess.CalledProcessError:
            print("[-] Failed to obfuscate payload with ASAF")
        return out_filename
