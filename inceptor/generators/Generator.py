import os
import sys
from abc import ABC, abstractmethod

from encoders.EncoderChain import EncoderChain


class Generator(ABC):
    def __init__(self, file, chain=None):
        self.file = file
        if not os.path.isfile(file):
            print(f"[-] Error reading input file")
            sys.exit(1)

        self.chain = chain
        if not chain:
            self.chain = EncoderChain()

    @abstractmethod
    def generate(self):
        pass
