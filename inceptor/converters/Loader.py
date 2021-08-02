import base64
import os
import re
import subprocess
import sys

from converters.Transformer import Transformer


class Loader(Transformer):
    def __init__(self):
        super().__init__()
        self.filetype = "raw"

    def transform(self, target):
        with open(target, 'rb') as content:
            return content.read()
