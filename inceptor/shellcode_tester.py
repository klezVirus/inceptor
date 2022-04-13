import argparse
import os
import subprocess
from ctypes import c_int, pointer, windll, c_uint64, create_string_buffer

import objdump
from enums.Architectures import Arch
from utils.utils import get_project_root, is_os_64bit

PAGE_EXECUTE_READWRITE = 0x00000040
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)
kernel32 = windll.kernel32

SPLIT_TEST = b"\xeb\x01\x90\x90\x90"  # JMP SHORT 0x3; nop; nop; nop


def execute(shellcode, arch=Arch.x64):
    print(f"[+] Executing the shellcode:{type(shellcode[0]).__name__} in a new thread")
    input("[*] Press a key to continue...")
    shellcode = bytes(shellcode)
    print(shellcode)
    if arch == Arch.x64:
        kernel32.VirtualAlloc.restype = c_uint64
    ptr = kernel32.VirtualAlloc(0, len(shellcode), VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
    if arch == Arch.x64:
        kernel32.RtlMoveMemory(
            c_uint64(ptr),
            create_string_buffer(shellcode),
            len(shellcode)
        )
        ht = kernel32.CreateThread(0, 0, c_uint64(ptr), 0, 0, 0)
        kernel32.WaitForSingleObject(ht, -1)
    else:
        kernel32.RtlMoveMemory(
            c_int(ptr),
            shellcode,
            c_int(len(shellcode))
        )
        ht = kernel32.CreateThread(c_int(0), c_int(0), c_int(ptr), c_int(0), c_int(0), pointer(c_int(0)))
        kernel32.WaitForSingleObject(c_int(ht), c_int(-1))


def split(file, split_len, arch=Arch.x64):
    dumper = objdump.ObjectDumper(arch=arch)

    shellcode = bytearray()
    chunks = dumper.objdump(file)
    length = 0
    for c in chunks:
        length += len(c)
        if length >= split_len:
            shellcode += SPLIT_TEST
            length = 0
        shellcode += c
    return bytes(shellcode)


def main(args):
    file = args.get("file")
    if args.get("split") > 0:
        shellcode = split(file, args.get("split"))
    else:
        with open(file, "rb") as shf:
            shellcode = shf.read()
    arch = Arch.from_string(args.get("arch"))
    if args.get("debug"):
        shellcode = b"\xcc" + shellcode
        debug(arch=arch)
    execute(shellcode, arch=arch)


def debug(autorun=True, args=None, arch=Arch.x64):
    print("[+] Opening WinDbg to test the shellcode")
    pid = os.getpid()
    custom_wew = get_project_root().joinpath("workspaces", "custom.wew")

    cmd = f"\"C:\\Program Files{' (x86)' if is_os_64bit() else ''}\\Windows Kits\\10\\Debuggers\\{arch.value}\\windbg.exe\" " \
          f"-WF \"{custom_wew}\" -p {pid} -c \".load pykd.pyd; {';'.join(args) + ';' if args else ''} g;\""
    print(cmd)
    if autorun:
        subprocess.Popen(
            cmd,
            shell=True,
            creationflags=subprocess.DETACHED_PROCESS,
            close_fds=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Shellcode Tester")
    parser.add_argument("file", help="Shellcode file")
    parser.add_argument("-a", "--arch", choices=["x86", "x64"], default="x64", required=False,
                        help="Shellcode Architecture")
    parser.add_argument("-d", "--debug", action='store_true', required=False,
                        help="Add int3 to the shellcode and debug with WinDbg")
    parser.add_argument("-i", "--inject", action='store_true', required=False,
                        help="Add int3 to the shellcode and debug with WinDbg")
    parser.add_argument("-s", "--split", type=int, required=False, default=0,
                        help="Try to split shellcode in chunks of minimum X bytes")
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args = parse_args()
    main(args)
