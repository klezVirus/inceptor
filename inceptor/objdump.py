import argparse
import binascii
from pathlib import Path

from capstone import *

from enums.Architectures import Arch

shellcode_here = ""


class ObjectDumper:
    def __init__(self, arch: Arch = Arch.x64, start: int = 0):
        self.arch = CS_MODE_32 if arch == Arch.x86 else CS_MODE_64
        self.start = start

    def objdump(self, file):
        path = Path(file)
        if not path.is_file():
            raise FileNotFoundError
        with open(str(path), "rb") as binary:
            code = binary.read()
        md = Cs(CS_ARCH_X86, self.arch)
        for i in md.disasm(code, self.start):
            # print([a for a in i.__dir__() if not a.startswith("__")])
            line = binascii.hexlify(i.bytes).decode()
            human = " ".join([line[i:i+2] for i in range(0, len(line), 2)])
            print(f"0x{i.address:08X}  {human:32} {i.mnemonic} {i.op_str}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="objdump: Windows tool to dump object into ASM", add_help=True)
    parser.add_argument("-L", "--length", required=False, type=int, default=0x0000,
                        help="Length of bytes to disassemble")
    parser.add_argument('-a', '--arch', required=False, type=str, choices=["x86", "x64"], default="x64",
                        help='Architecture')
    parser.add_argument('file', type=str, help='Path to file to disassemble')
    args = parser.parse_args()

    arch = Arch.from_string(args.arch)

    objdump = ObjectDumper(arch=arch, start=args.length)

    objdump.objdump(file=args.file)
