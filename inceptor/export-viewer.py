import argparse
import os

from utils.export_wiewer import ExportViewer
from utils.utils import detect_arch

if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(description=r"A simple DLL Export viewer", add_help=True)
    parser.add_argument("target", help="The DLL to analyze")
    parser.add_argument("-f", "--filter", required=False, type=str, default=None,
                        help="Filter output for a pattern")
    parser.add_argument("-d", "--disas", required=False, type=str, default=None,
                        help="Disassemble given function, if found")
    parser.add_argument("-v", "--verbose", required=False, action='store_true',
                        help="Shows raw output (doesn't work with a filter set)")
    args = parser.parse_args()

    if os.path.isfile(args.target):
        arch = detect_arch(args.target)
        expviewer = ExportViewer(arch=arch)
        expviewer.check(args.target, match=args.filter, verbose=args.verbose)
        expviewer.dump(args.disas)
    else:
        raise FileNotFoundError("No such file")
