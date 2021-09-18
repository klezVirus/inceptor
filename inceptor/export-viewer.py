import argparse
import os

from utils.export_wiewer import ExportViewer
from utils.utils import detect_arch

if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(description=r"A simple DLL Export viewer", add_help=True)
    parser.add_argument("target", help="The DLL to analyze")
    parser.add_argument("-v", "--verbose", required=False, action='store_true', help="Shows full output")
    args = parser.parse_args()

    if os.path.isfile(args.target):
        arch = detect_arch(args.target)
        expviewer = ExportViewer(arch=arch)
        expviewer.check(args.target, verbose=args.verbose)
    else:
        raise FileNotFoundError("No such file")
