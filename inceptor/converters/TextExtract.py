import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import pefile

import utils.utils
from compilers.ClCompiler import ClCompiler
from compilers.MasmCompiler import MasmCompiler
from config.Config import Config
from converters.Transformer import Transformer
from utils.console import Console


class TextExtract(Transformer):
    def __init__(self):
        super().__init__()
        self.filetype = "cpp"

    def transform(self, target):
        Console.auto_line("[*] Loading transformer auto-procedure")

        align_stack_routine = utils.utils.static_random_ascii_string(5, 7)
        asm_raw = utils.utils.get_temporary_file(".asm")
        outfile = utils.utils.strip_file_extension(asm_raw) + ".exe"
        masm = MasmCompiler()
        masm.set_link_only()
        masm.set_entry(align_stack_routine)
        masm.set_output_file(outfile)
        Console.auto_line("[*] Compiling object file")

        cl = ClCompiler()
        cl.set_compilation_to_asm(asm_raw)
        if not cl.compile([target]):
            Console.auto_line("[-] Failed to generate object file")
        compiled_file = os.path.basename(utils.utils.strip_file_extension(target) + ".asm")
        if os.path.isfile(compiled_file):
            shutil.move(compiled_file, asm_raw)

        Console.auto_line("[*] Fixing issues in auto-generated assembly file")
        input()
        with open(asm_raw, "r") as af:
            asm_code = af.read()
        asm_code = re.sub(r"_TEXT\s*SEGMENT", rf"""_TEXT    SEGMENT

{align_stack_routine} PROC
    push rdi                    ; backup rdi since we will be using this as our main register
    mov rdi, rsp                ; save stack pointer to rdi
    and rsp, 0FFFFFFFFFFFFFFF0h ; align stack with 16 bytes
    sub rsp, 020h               ; allocate some space for our C function
    call main                   ; call the C function
    mov rsp, rdi                ; restore stack pointer
    pop rdi                     ; restore rdi
    ret                         
{align_stack_routine} ENDP

        """, asm_code, 1)
        asm_code = re.sub(r"[x|p]data\s*SEGMENT[\w|\W]+[x|p]data\sENDS", "", asm_code)
        asm_code = re.sub(r"INCLUDELIB\s*[\w]+", "", asm_code)
        asm_code = asm_code.replace("gs:96", "gs:[96]")
        asm_code = asm_code.replace("include listing.inc", "; include listing.inc")
        asm_code = asm_code.replace("FLAT:", "")
        asm_code = re.sub(r"EXTRN\s*__chkstk:PROC\s", "", asm_code)
        asm_code = re.sub(r"call\s*__chkstk\s", "", asm_code)
        with open(asm_raw, "w") as af:
            af.write(asm_code)

        Console.auto_line("[*] Linking assembly file")
        if not masm.compile([asm_raw]):
            Console.auto_line("[-] Failed to generate final exe file")
            exit(1)

        raw = None
        pe = pefile.PE(outfile)
        for section in pe.sections:
            if section.Name == b".text\x00\x00\x00":
                if self.debug:
                    print(
                        f"{section.Name}: {hex(section.VirtualAddress)}, "
                        f"{hex(section.Misc_VirtualSize)}, {section.SizeOfRawData}"
                    )
                raw = section.get_data()
        if not raw:
            Console.auto_line("[-] Failed to extract .text section")
        return raw

