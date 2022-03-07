import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from config.Config import Config
from encoders.EncoderChain import EncoderChain
from signers.Signer import Signer
from utils.Koppeling import Koppeling
from utils.MetaTwin import MetaTwin
from utils.console import Console
from utils.utils import get_project_root


class Generator(ABC):
    def __init__(self, file, chain=None):
        self.file = file
        self.clone = None
        if not os.path.isfile(file):
            print(f"[-] Error reading input file")
            sys.exit(1)

        self.chain = chain
        if not chain:
            self.chain = EncoderChain()

    @abstractmethod
    def generate(self):
        pass

    def sign(self, signee, signed, domain=None, offline=False, clone=None):
        if not domain:
            host = Config().get("SIGNING", "domain")
        else:
            host = domain
        if offline and clone:
            shutil.copy(signee, signed)
            signer_class = Signer.from_name("SigThief")
            signer = signer_class(action="clone")
            signer.sign(signee=clone, signed=signed)
        elif offline:
            signer_class = Signer.from_name("LazySign")
            signer = signer_class(verbose=False, host=host)
            signer.sign(signee=signee, signed=signed)
        else:
            signer_class = Signer.from_name("CarbonCopy")
            signer = signer_class(verbose=False, host=host)
            signer.sign(signee=signee, signed=signed)
        Console.auto_line(f"  [+] Signed with: {signer_class.__name__}")

    def clone_metadata(self, target: Path):
        if not (self.clone and self.clone.is_file()):
            return False
        meta_twin = MetaTwin()
        meta_twin.clone(str(self.clone.absolute()), target)

    def clone_exports(self, target: Path):
        if not (self.clone and self.clone.is_file()):
            return False
        koppeling = Koppeling()
        koppeling.clone_exports(str(self.clone.absolute()), target)
