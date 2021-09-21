import os.path
import tempfile

import pefile
import argparse
import os
import subprocess
import sys

from config.Config import Config
from utils.console import Console
from win32_setctime import setctime


class MetaTwin:
    def __init__(self):
        self.path = str(Config().get_path("DIRECTORIES", f"libs").joinpath("ResourceHacker.exe"))
        self.debug = Config().get_boolean("DEBUG", "utilities")
        self.copy_from = None
        self.copy_to = None

    def timestomp(self, copy_from, copy_to):
        st_mtime = os.stat(copy_from).st_mtime
        st_atime = os.stat(copy_from).st_atime
        st_ctime = os.stat(copy_from).st_ctime
        os.utime(copy_to, (st_atime, st_mtime))
        setctime(copy_to, st_ctime)

    def clone(self, copy_from, copy_to):
        self.copy_from = copy_from
        self.copy_to = copy_to

        base_name = os.path.basename(tempfile.NamedTemporaryFile(prefix="resources").name)
        log_file = Config().get_path("DIRECTORIES", f"writer").joinpath(f"{base_name}.log")
        resource_file = Config().get_path("DIRECTORIES", f"writer").joinpath(f"{base_name}.res")
        rc_file = Config().get_path("DIRECTORIES", f"writer").joinpath(f"{base_name}.rc")

        if not os.path.isfile(copy_from):
            Console.auto_line(f"[-] MetaTwin: Source File {copy_from} not found")
            sys.exit(1)

        steps = [
            [
                f"Extracting Resources from '{copy_from}'",
                f"\"{self.path}\" -open \"{copy_from}\" -action extract -mask ,,, -save \"{resource_file}\" -log \"{log_file}\"",
                "Error extracting resources"
            ],
            [
                f"Copying Resources to '{copy_to}'",
                f"\"{self.path}\" -open \"{copy_to}\" -log \"{log_file}\" -action addoverwrite -res \"{resource_file}\" -mask ,,, -save \"{copy_to}\"",
                "Error copying resources"
            ]
        ]

        for step in steps:
            try:
                if self.debug:
                    Console.auto_line(f"[*] {step[0]}")
                cmd = step[1]
                if self.debug:
                    Console.auto_line(f"  [>] MetaTwin cmdline: {cmd}")
                output = subprocess.check_output(cmd, shell=True).decode().rstrip()
                if self.debug:
                    Console.auto_line(output)
            except subprocess.CalledProcessError as e:
                Console.auto_line(f"  [-] Error: {step[2]}")
                continue
        rc_file.unlink(missing_ok=True)
        resource_file.unlink(missing_ok=True)
        log_file.unlink(missing_ok=True)

    def compare(self, source):
        pass

    def inspect(self, target, dump=False):
        """
        Read all metadata from a file
        """
        source = pefile.PE(target)
        """
        destination = pefile.PE(copy_to)
        company_name = ""
        product_name = ""
        _bytes = destination.write()

        setattr(destination, "VS_VERSIONINFO", None)
        setattr(destination, "VS_FIXEDFILEINFO", None)
        setattr(destination, "FileInfo", None)

        destination.VS_VERSIONINFO = source.VS_VERSIONINFO.copy()
        destination.VS_FIXEDFILEINFO = source.VS_FIXEDFILEINFO.copy()
        destination.__structures__.append(destination.VS_VERSIONINFO[0])
        destination.__structures__.append(destination.VS_FIXEDFILEINFO[0])
        destination.FileInfo = source.FileInfo.copy()
        """
        dumped = {}
        for fileinfo in source.FileInfo:
            if fileinfo[0].name == 'StringFileInfo':
                for st in fileinfo[0].StringTable:
                    for entry in st.entries.items():
                        key, value = entry[0].decode(), entry[1].decode()
                        if dump:
                            dumped[key] = value
                        print(f'{key}: {value}')
        return dumped
