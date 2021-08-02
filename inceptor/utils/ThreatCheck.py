import os
import re
import subprocess
import sys
from datetime import datetime

from config.Config import Config
from utils.console import Console
from utils.utils import get_project_root


class ThreatCheck:
    def __init__(self):
        self.engines = ["Defender", "AMSI"]
        self.path = str(Config().get_path("DIRECTORIES", "libs").joinpath("ThreatCheck.exe"))

    def check(self, filename):
        Console.auto_line(f"[+] Starting ThreatCheck Scan At {datetime.utcnow()}")
        if not os.path.isfile(filename):
            Console.auto_line(f"[-] ThreatCheck: File {filename} not found")
            sys.exit(1)
        for engine in self.engines:
            try:
                cmd = f"\"{self.path}\" -f {filename} -e {engine}"
                # print(cmd)
                output = subprocess.check_output(cmd).decode().rstrip()
                if output.find("No threat found") >= 0:
                    Console.auto_line(f"  [+] SUCCESS: {engine} Bypassed!")
                elif output.find("Ensure real-time protection is enabled") >= 0:
                    Console.auto_line("  [#] UNKNOWN: Real-Time Protection Disabled")
                else:
                    Console.auto_line(f"  [-] FAILED: {engine} Triggered!")
            except subprocess.CalledProcessError as e:
                for line in e.output.decode().split("\n"):
                    if re.search(r"error", line):
                        print(f"  [-] Error: {line}")
                        continue
        Console.auto_line(f"[+] ThreatCheck Scan Finished At {datetime.utcnow()}")
