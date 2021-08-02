import base64
import os
import re
import subprocess
import sys
from abc import ABC, abstractmethod


class Transformer(ABC):

    def __init__(self):
        super(Transformer, self).__init__()
        self.filetype = None

    @abstractmethod
    def transform(self, target):
        pass

    def set_architecture(self, arch="x64"):
        pass
