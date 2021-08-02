#!/usr/bin/python3

import argparse
import json
import os
import random
import shutil
import struct

from config.Config import Config
from utils.utils import get_project_root


class SysWhispers(object):
    def __init__(self):
        self.basepath = os.path.join(get_project_root(), 'syscalls', 'syswhispersv2_x86', 'x86')

    def generate(self, basename: str = 'syscalls'):
        for ext in [".c", ".h", ".asm"]:
            file = os.path.join(self.basepath, f"Syscalls{ext}")
            dest = f"{basename}{ext}"
            if ext == ".c":
                with open(dest, "w") as out:
                    content = open(file, "r").read()
                    content = content.replace("####HEADER####", dest.replace(".c", ".h"))
                    out.write(content)
            else:
                shutil.copy(file, dest)


