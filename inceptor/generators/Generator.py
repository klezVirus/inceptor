import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from encoders.EncoderChain import EncoderChain
from utils.MetaTwin import MetaTwin


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

    def clone_metadata(self, target: Path):
        if not (self.clone and self.clone.is_file()):
            return False
        meta_twin = MetaTwin()
        meta_twin.clone(str(self.clone.absolute()), target)
