import argparse
import os
import subprocess
from ctypes import c_int, pointer, windll

from utils.utils import get_project_root, is_os_64bit

PAGE_EXECUTE_READWRITE = 0x00000040
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)
kernel32 = windll.kernel32


def execute(shellcode):
    print(f"[+] Executing the shellcode:{type(shellcode[0]).__name__} in a new thread")
    input("[*] Press a key to continue...")
    shellcode = bytes(shellcode)
    print(shellcode)
    ptr = kernel32.VirtualAlloc(0, len(shellcode), VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
    kernel32.RtlMoveMemory(
        c_int(ptr),
        shellcode,
        c_int(len(shellcode))
    )
    ht = kernel32.CreateThread(c_int(0), c_int(0), c_int(ptr), c_int(0), c_int(0), pointer(c_int(0)))
    kernel32.WaitForSingleObject(c_int(ht), c_int(-1))


def main(args):
    with open(args.get("file"), "rb") as shf:
        shellcode = shf.read()
    if args.get("debug"):
        shellcode = b"\xcc" + shellcode
        debug()
        execute(shellcode)


def debug(autorun=True, args=None, arch="x64"):
    print("[+] Opening WinDbg to test the shellcode")
    pid = os.getpid()
    custom_wew = get_project_root().joinpath("workspaces", "custom.wew")

    cmd = f"\"C:\\Program Files{' (x86)' if is_os_64bit() else ''}\\Windows Kits\\10\\Debuggers\\{arch}\\windbg.exe\" " \
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
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args = parse_args()
    main(args)
