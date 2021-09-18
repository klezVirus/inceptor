import argparse
import os
import subprocess
import sys
from datetime import datetime

from config.Config import Config
from enums.Architectures import Arch
from utils.console import Console
from utils.utils import detect_arch


class ExportViewer:
    def __init__(self, arch=Arch.x64):
        self.path = str(Config().get_path("DUMPERS", f"dumpbin_{arch.value}"))

    def check(self, filename, verbose=False):
        Console.auto_line(f"[+] Starting Export Viewer At {datetime.utcnow()}")
        if not os.path.isfile(filename):
            Console.auto_line(f"[-] Export Viewer: Target File {filename} not found")
            sys.exit(1)
        try:
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
                        results.append([x for x in line.rstrip("\r\n").split(" ") if x.strip() != ""])
                from tabulate import tabulate
                Console.auto_line(tabulate(results, headers=headers))
        except subprocess.CalledProcessError as e:
            Console.auto_line(f"  [-] Error: {e}")
        Console.auto_line(f"[+] Export Viewer Finished At {datetime.utcnow()}")

