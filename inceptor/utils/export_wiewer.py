import argparse
import os
import pefile
import re
import subprocess
import sys
from datetime import datetime

from capstone import *

import utils.utils
from config.Config import Config
from enums.Architectures import Arch
from utils.console import Console
from utils.utils import detect_arch


class ExportViewer:
    def __init__(self, arch=Arch.x64):
        self.path = str(Config().get_path("DUMPERS", f"dumpbin_{arch.value}"))
        self.rva2func = {}
        self.pe = None
        self.data = None
        self.entry_point = None
        self.arch = Arch.x64

    def check(self, filename, match: str = None, verbose=False):
        if match:
            verbose = False
        Console.auto_line(f"[+] Starting Export Viewer At {datetime.utcnow()}")
        if not os.path.isfile(filename):
            Console.auto_line(f"[-] Export Viewer: Target File {filename} not found")
            sys.exit(1)
        try:
            self.pe = pefile.PE(filename)
            self.entry_point = self.pe.OPTIONAL_HEADER.AddressOfEntryPoint
            self.data = self.pe.get_memory_mapped_image()[self.entry_point:]

            cmd = f"\"{self.path}\" -EXPORTS \"{filename}\""
            # print(cmd)
            output = subprocess.check_output(cmd).decode().rstrip()
            if verbose:
                Console.auto_line(output)
            else:
                do_print = False
                headers = []
                results = []
                for line in output.split("\n"):
                    row = []
                    if line.find("ordinal") > -1 and line.find("hint") > -1:
                        headers = [x for x in line.rstrip("\r\n").split(" ") if x.strip() != ""]
                        do_print = True
                        continue
                    elif line.find("Summary") > -1:
                        do_print = False
                    if do_print:
                        results.append([x for x in line.rstrip("\r\n").split(" ") if len(x) > 0])
                from tabulate import tabulate
                if match:
                    matcher = re.compile(match) if match else re.compile(r".*")
                    results = [x for x in results if len(x) == 4 and matcher.search(x[3])]
                for r in results:
                    if len(r) == 4:
                        self.rva2func[r[3]] = r[2]
                Console.auto_line(tabulate(results, headers=headers))
        except subprocess.CalledProcessError as e:
            Console.auto_line(f"  [-] Error: {e}")
        Console.auto_line(f"[+] Export Viewer Finished At {datetime.utcnow()}")

    def dump(self, function=None):
        if not function:
            return
        for k, v in self.rva2func.items():
            if function != k:
                continue
            Console.auto_line(f"[*] Disassembling {k}...")
            if self.arch == Arch.x86:
                md = Cs(CS_ARCH_X86, CS_MODE_32)
            else:
                md = Cs(CS_ARCH_X86, CS_MODE_64 + CS_MODE_LITTLE_ENDIAN)
            md.detail = True
            md.syntax = CS_OPT_SYNTAX_INTEL
            md.skipdata_setup = ("db", None, None)
            md.skipdata = True

            '''
            Maybe I'll use this if I want a full-python utility (no dumpbin)
            ----------------------------------------------------------------
            for exp in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if exp.name.decode('utf-8') == function:
                    print(hex(self.pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name.decode('utf-8'))
                    for i in md.disasm(self.data, self.pe.OPTIONAL_HEADER.ImageBase + exp.address, 20):
                        print(f"0x{i.address:08x}\t{i.mnemonic}\t{i.op_str}")
            sys.exit(1)
            '''
            # This is not working properly
            for i in md.disasm(self.data, self.pe.OPTIONAL_HEADER.ImageBase + int(v, 16), 20):
                print(f"0x{i.address:08x}\t{i.mnemonic}\t{i.op_str}")

