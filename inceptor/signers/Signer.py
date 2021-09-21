import os
import sys
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from pydoc import locate

from config.Config import Config
from encoders.EncoderChain import EncoderChain
from enums.Architectures import Arch
from utils.utils import get_project_root


class Signer(ABC):
    TIMESTAMP_URL_T = "http://timestamp.comodoca.com/authenticode"
    TIMESTAMP_URL_TR = "http://sha256timestamp.ws.symantec.com/sha256/timestamp"

    def __init__(self, host='www.microsoft.com', port='443', arch=Arch.x64, banner=False, verbose=False):
        self.config = Config()
        self.verbose = verbose
        self.banner = banner
        self.host = host
        self.port = port
        self.arch = arch
        self.certificate_directory = Path(os.path.join(get_project_root(), "certs"))

    @abstractmethod
    def sign(self, signee, signed):
        pass

    @staticmethod
    def from_name(name: str):
        try:
            signer_class_string = f"signers.{name}.{name}"
            signer_class = locate(signer_class_string)
            return signer_class
        except:
            traceback.print_exc()
            pass
