import hashlib
import os
import re
import secrets
import subprocess
import sys
import tempfile
from binascii import hexlify, unhexlify
from enum import Enum
from random import random, randint

from pefile import *
from pathlib import Path
import struct

from enums.Architectures import Arch


class ImageFileMachine(Enum):
    IMAGE_FILE_MACHINE_I386 = 332
    IMAGE_FILE_MACHINE_IA64 = 512
    IMAGE_FILE_MACHINE_AMD64 = 34404

    @staticmethod
    def from_bytes(_bytes: bytes):
        if len(_bytes) > 2:
            _bytes = _bytes[:2]
        machine = struct.unpack("<H", _bytes)[0]
        if machine == ImageFileMachine.IMAGE_FILE_MACHINE_I386.value:
            return Arch.x86
        elif machine == ImageFileMachine.IMAGE_FILE_MACHINE_IA64.value:
            return Arch.x64
        elif machine == ImageFileMachine.IMAGE_FILE_MACHINE_AMD64.value:
            return Arch.x64
        else:
            _hex_value = hexlify(struct.pack('H', machine)).decode()
            raise ValueError(
                f"Unknown architecture.\n"
                f"  Raw: {struct.pack('H', machine)}\n"
                f"  Hex: {_hex_value[:2]} {_hex_value[2:]}"
            )


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def bin2sh(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError("[-] Missing Bin2Sh target file")
    utility = os.path.join(get_project_root(), "libs", "public", "adon.exe")
    if not os.path.isfile(utility):
        raise FileNotFoundError("[-] Missing Bin2Sh utility file")
    return subprocess.check_output(f"{utility} \"{filename}\"").decode().strip()


def bin2hex4pe2sh(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError("[-] Missing bin2hex (pe2sh) target file")
    utility = os.path.join(get_project_root(), "libs", "public", "chunlie.exe")
    if not os.path.isfile(utility):
        raise FileNotFoundError("[-] Missing bin2hex (pe2sh) utility file")
    return unhexlify(subprocess.check_output(f"{utility} \"{filename}\"").decode().strip())


def py_bin2sh(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError("[-] Missing PyBin2Sh target file")
    content = hexlify(open(filename, "rb").read()).decode()
    shellcode = "{" + ",".join([f"0x{content[i:i + 2]}" for i in range(0, len(content), 2)]) + "}"
    return shellcode


def sgn(shellcode, arch="x64"):
    architecture = "64" if arch in ["x64", None] else "32"
    filename = None
    temp_filename = tempfile.NamedTemporaryFile(suffix=".raw",
                                                delete=False,
                                                dir=os.path.join(get_project_root(), "temp")).name
    with open(temp_filename, "wb") as temp:
        temp.write(shellcode)
    if not os.path.isfile(temp_filename):
        raise FileNotFoundError("[-] Missing Shikata-Ga-Nai target file")
    utility = os.path.join(get_project_root(), "libs", "public", "sgn.exe")
    if not os.path.isfile(utility):
        raise FileNotFoundError("[-] Missing Shikata-Ga-Nai utility file")
    try:
        cmd = f"{utility} -safe -a {architecture} \"{temp_filename}\""
        # print(cmd)
        output = subprocess.check_output(cmd).decode().strip()
        for line in output.split("\n"):
            if line.find("Outfile:") > - 1:
                filename = line.split(": ")[1]
                print(f"    [*] Encoded filename: {filename}")
                shellcode = open(filename, "rb").read()
    except subprocess.CalledProcessError:
        print("[-] Failed to encode payload with Shikata-Ga-Nai")
    if os.path.isfile(temp_filename):
        os.unlink(temp_filename)
    if filename and os.path.isfile(filename):
        os.unlink(filename)
    return shellcode


def isDotNet(filename):
    try:
        pe = PE(filename)
        clr_metadata = pe.OPTIONAL_HEADER.DATA_DIRECTORY[14]
        return not (clr_metadata.VirtualAddress == 0 and clr_metadata.Size == 0)
    except PEFormatError:
        return False


def shellcode_signature(shellcode):
    if isinstance(shellcode, str):
        shellcode = shellcode.encode()
    return hashlib.sha1(shellcode).hexdigest()


def file_signature(filename):
    _, ext = os.path.splitext(filename)
    with open(filename, "rb") as file:
        signature = hashlib.sha1(file.read()).hexdigest()
    return signature


def choose(choices: list):
    for n, ver in enumerate(choices):
        print(f"  {n}: {ver}")
    choice = -1
    while not (0 <= choice < len(choices)):
        try:
            choice = int(input("> "))
            return choices[choice]
        except ValueError:
            continue
        except TypeError:
            continue


def mssql_hex(file):
    with open(file=file, mode="rb") as dll:
        content = dll.read()
    return f"0x{hexlify(content).decode()}"


def static_random_ascii_string(min_size=None, max_size=None):
    if not min_size:
        min_size = 3
    if not max_size:
        max_size = 10
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(randint(min_size, max_size)))


def detect_arch(file):
    f = open(file, "rb").read()

    if f[:2] != b"MZ":
        print("[-] Unknown file format")
        sys.exit(1)
    else:
        header_offset = struct.unpack("<L", f[60:64])[0]
        raw = f[header_offset + 4:header_offset + 6]
        return ImageFileMachine.from_bytes(raw)


def get_temporary_file(ext=None):
    return tempfile.NamedTemporaryFile(
        dir=os.path.join(get_project_root(), "temp"),
        suffix=ext if ext else "",
        delete=True
    ).name


if __name__ == '__main__':
    try:
        payload = mssql_hex(sys.argv[1])
        if len(payload) <= 8000:
            print("[+] Success. payload length is under MAX_LENGTH")
        else:
            print(f"[-] Warning: payload length is above MAX_LENGTH: {len(payload)}")
        print(payload)
    except:
        print("[-] Error: MSSQL Hexlify needs a file to encode")
