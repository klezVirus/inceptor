import os
import subprocess

from config.Config import Config
from obfuscators.Obfuscator import Obfuscator
from obfuscators.powershell.chameleon.chameleon import Chameleon
from utils.utils import get_project_root


class Karmaleon(Obfuscator):
    def __init__(self, filename, outfile):
        path = None
        args = {}
        super().__init__(sep=" ", path=path, args=args)
        self.filename = filename
        self.outfile = outfile

        if not os.path.isfile(filename):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator target file")

    def obfuscate(self):
        level = 0
        config = {
            "strings": True,
            "variables": True,
            "data-types": True,
            "functions": True,
            "comments": True,
            "spaces": True,
            "cases": True,
            "nishang": True,
            "backticks": True,
            "random-backticks": False,
            "backticks-list": [],
            "hex-ip": True,
            "random-type": "r",
            "decimal": False,
            "base64": False,
            "tfn-values": False,
            "safe": False,
            "verbose": False
        }

        chameleon = Chameleon(filename=self.filename, outfile=self.outfile, config=config, quiet=True)
        chameleon.obfuscate()
        chameleon.write_file()
        return self.outfile
