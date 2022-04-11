import base64
import os
import re
import subprocess
import sys
import pefile

import utils.utils
from config.Config import Config
from converters.Transformer import Transformer
from utils.console import Console


class TextExtract(Transformer):
    def __init__(self):
        super().__init__()
        self.filetype = "exe"

    def transform(self, target):
        align_stack_file = Config().get_path("DIRECTORIES", "WRITER").joinpath("alignstack.asm")
        linker_script = utils.utils.get_temporary_file("asm")
        raw = None
        pe = pefile.PE(target)
        for section in pe.sections:
            if section.name == ".text":
                if self.debug:
                    print(
                        f"{section.Name}: {hex(section.VirtualAddress)}, "
                        f"{hex(section.Misc_VirtualSize)}, {section.SizeOfRawData}"
                    )
                raw = section.get_data()
        if not raw:
            Console.auto_line("[-] Failed to extract .text section")
        with open(str(align_stack_file), "w") as asf:
            asf.write(r"""
; Copied from ParanoidNinja blog post
extern run
global alignstack

segment .text

alignstack:
    push rdi                    ; backup rdi since we will be using this as our main register
    mov rdi, rsp                ; save stack pointer to rdi
    and rsp, byte -0x10         ; align stack with 16 bytes
    sub rsp, byte +0x20         ; allocate some space for our C function

    ; If we have a single params pointer argument in rcx, we should be able to just 
    ; use it immediately in run()

    call run                    ; call the C function
    mov rsp, rdi                ; restore stack pointer
    pop rdi                     ; restore rdi
    ret                         
            """)

        with open(linker_script, "w") as ls:
            ls.write(r"""
 ENTRY(alignstack)
    SECTIONS
    {
        .text :
        {
            *(.text.alignstack)
            *(.text.getprivs)
        }
    }
    
            """)
