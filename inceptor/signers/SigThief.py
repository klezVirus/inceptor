#!/usr/bin/env python3
# LICENSE: BSD-3
# Copyright: Josh Pitts @midnite_runr
# Adapted by klezVirus @klezVirus

import argparse
import os.path
import sys
import struct
import shutil
import io
import tempfile
from pathlib import Path

from config.Config import Config
from utils.console import Console


class SigThief:

    ACTIONS = ["save", "add", "del", "check", "clone"]

    def __init__(self, action, certificate_file=None):
        self.config = Config()
        self.debug = self.config.get_boolean("DEBUG", "signers")
        self.action = action
        self.certificate_file = certificate_file
        self.certificate = None
        if not certificate_file:
            self.certificate_file = tempfile.NamedTemporaryFile(
                dir=str(self.config.get_path("DIRECTORIES", "certificates")),
                suffix=".cer",
                delete=True
            ).name
        elif certificate_file and action == "add":
            self.certificate = open(self.certificate_file, "rb").read()
        self.target_info = {}

    @property
    def suffix(self):
        if self.action in ["add", "clone"]:
            return "_signed"
        elif self.action in ["save"]:
            return "_sig"
        elif self.action in ["del"]:
            return "_nosig"

    def clean(self):
        if self.action != "save":
            path = Path(self.certificate_file)
            path.unlink(missing_ok=True)

    def __gather_file_info_win(self, file):
        """
        Borrowed from BDF...
        I could just skip to certLOC... *shrug*
        """
        if self.debug:
            Console.auto_line(f"[*] Gathering binary information: '{file}'")
        self.target_info = {}
        with open(file, 'rb') as binary:
            binary.seek(int('3C', 16))
            self.target_info['buffer'] = 0
            self.target_info['JMPtoCodeAddress'] = 0
            self.target_info['dis_frm_pehdrs_sectble'] = 248
            self.target_info['pe_header_location'] = struct.unpack('<i', binary.read(4))[0]
            # Start of COFF
            self.target_info['COFF_Start'] = self.target_info['pe_header_location'] + 4
            binary.seek(self.target_info['COFF_Start'])
            self.target_info['MachineType'] = struct.unpack('<H', binary.read(2))[0]
            binary.seek(self.target_info['COFF_Start'] + 2, 0)
            self.target_info['NumberOfSections'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['TimeDateStamp'] = struct.unpack('<I', binary.read(4))[0]
            binary.seek(self.target_info['COFF_Start'] + 16, 0)
            self.target_info['SizeOfOptionalHeader'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['Characteristics'] = struct.unpack('<H', binary.read(2))[0]
            # End of COFF
            self.target_info['OptionalHeader_start'] = self.target_info['COFF_Start'] + 20

            # if self.target_info['SizeOfOptionalHeader']:
            # Begin Standard Fields section of Optional Header
            binary.seek(self.target_info['OptionalHeader_start'])
            self.target_info['Magic'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['MajorLinkerVersion'] = struct.unpack("!B", binary.read(1))[0]
            self.target_info['MinorLinkerVersion'] = struct.unpack("!B", binary.read(1))[0]
            self.target_info['SizeOfCode'] = struct.unpack("<I", binary.read(4))[0]
            self.target_info['SizeOfInitializedData'] = struct.unpack("<I", binary.read(4))[0]
            self.target_info['SizeOfUninitializedData'] = struct.unpack("<I",
                                                                        binary.read(4))[0]
            self.target_info['AddressOfEntryPoint'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['PatchLocation'] = self.target_info['AddressOfEntryPoint']
            self.target_info['BaseOfCode'] = struct.unpack('<I', binary.read(4))[0]
            if self.target_info['Magic'] != 0x20B:
                self.target_info['BaseOfData'] = struct.unpack('<I', binary.read(4))[0]
            # End Standard Fields section of Optional Header
            # Begin Windows-Specific Fields of Optional Header
            if self.target_info['Magic'] == 0x20B:
                self.target_info['ImageBase'] = struct.unpack('<Q', binary.read(8))[0]
            else:
                self.target_info['ImageBase'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['SectionAlignment'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['FileAlignment'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['MajorOperatingSystemVersion'] = struct.unpack('<H',
                                                                            binary.read(2))[0]
            self.target_info['MinorOperatingSystemVersion'] = struct.unpack('<H',
                                                                            binary.read(2))[0]
            self.target_info['MajorImageVersion'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['MinorImageVersion'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['MajorSubsystemVersion'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['MinorSubsystemVersion'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['Win32VersionValue'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['SizeOfImageLoc'] = binary.tell()
            self.target_info['SizeOfImage'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['SizeOfHeaders'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['CheckSum'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['Subsystem'] = struct.unpack('<H', binary.read(2))[0]
            self.target_info['DllCharacteristics'] = struct.unpack('<H', binary.read(2))[0]
            if self.target_info['Magic'] == 0x20B:
                self.target_info['SizeOfStackReserve'] = struct.unpack('<Q', binary.read(8))[0]
                self.target_info['SizeOfStackCommit'] = struct.unpack('<Q', binary.read(8))[0]
                self.target_info['SizeOfHeapReserve'] = struct.unpack('<Q', binary.read(8))[0]
                self.target_info['SizeOfHeapCommit'] = struct.unpack('<Q', binary.read(8))[0]

            else:
                self.target_info['SizeOfStackReserve'] = struct.unpack('<I', binary.read(4))[0]
                self.target_info['SizeOfStackCommit'] = struct.unpack('<I', binary.read(4))[0]
                self.target_info['SizeOfHeapReserve'] = struct.unpack('<I', binary.read(4))[0]
                self.target_info['SizeOfHeapCommit'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['LoaderFlags'] = struct.unpack('<I', binary.read(4))[0]  # zero
            self.target_info['NumberofRvaAndSizes'] = struct.unpack('<I', binary.read(4))[0]
            # End Windows-Specific Fields of Optional Header
            # Begin Data Directories of Optional Header
            self.target_info['ExportTableRVA'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['ExportTableSize'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['ImportTableLOCInPEOptHdrs'] = binary.tell()
            # ImportTable SIZE|LOC
            self.target_info['ImportTableRVA'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['ImportTableSize'] = struct.unpack('<I', binary.read(4))[0]
            self.target_info['ResourceTable'] = struct.unpack('<Q', binary.read(8))[0]
            self.target_info['ExceptionTable'] = struct.unpack('<Q', binary.read(8))[0]
            self.target_info['CertTableLOC'] = binary.tell()
            self.target_info['CertLOC'] = struct.unpack("<I", binary.read(4))[0]
            self.target_info['CertSize'] = struct.unpack("<I", binary.read(4))[0]
        if self.debug:
            Console.auto_line(f"[+] Information successfully recovered")

    def copy_cert(self, signee):
        self.__gather_file_info_win(signee)
        if self.target_info['CertLOC'] == 0 or self.target_info['CertSize'] == 0:
            # not signed
            Console.auto_line("[-] Input file Not signed!")
            sys.exit(-1)
        with open(signee, 'rb') as f:
            f.seek(self.target_info['CertLOC'], 0)
            self.certificate = f.read(self.target_info['CertSize'])

    def sign(self, signee, signed):
        self.__gather_file_info_win(signee)
        if not self.certificate:
            self.copy_cert(signee)
        if self.debug:
            Console.auto_line("[*] Output file: {0}".format(signed))

        with open(signee, 'rb') as g:
            with open(signed, 'wb') as f:
                f.write(g.read())
                f.seek(0)
                f.seek(self.target_info['CertTableLOC'], 0)
                f.write(struct.pack("<I", len(open(signee, 'rb').read())))
                f.write(struct.pack("<I", len(self.certificate)))
                f.seek(0, io.SEEK_END)
                f.write(self.certificate)
        if self.debug:
            Console.auto_line("[+] Signature successfully appended")
        self.clean()

    def save_cert(self, exe):
        if not self.certificate:
            self.copy_cert(exe)
        if self.debug:
            Console.auto_line("[*] Output file: {0}".format(self.certificate_file))
        with open(self.certificate_file, 'wb') as c_out:
            c_out.write(self.certificate)
        if self.debug:
            Console.auto_line("[+] Signature ripped")

    def check_sig(self, signed, echo=True):
        self.__gather_file_info_win(signed)
        if self.target_info['CertLOC'] == 0 or self.target_info['CertSize'] == 0:
            # not signed
            if echo:
                Console.auto_line("[-] File not signed!")
            return False
        else:
            if echo:
                Console.auto_line("[+] File is signed!")
            return True

    def truncate(self, signed, unsigned):
        if not self.check_sig(signed):
            sys.exit(-1)

        shutil.copy2(signed, unsigned)

        with open(unsigned, "r+b") as binary:
            if self.debug:
                Console.auto_line('[*] Overwriting certificate table pointer and truncating binary')
            binary.seek(-self.target_info['CertSize'], io.SEEK_END)
            binary.truncate()
            binary.seek(self.target_info['CertTableLOC'], 0)
            binary.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        if self.debug:
            Console.auto_line("[+] Signature removed")

    def sign_with(self, certificate, signee, signed):
        self.certificate = open(certificate, 'rb').read()
        self.sign(signee, signed)

