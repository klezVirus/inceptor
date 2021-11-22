import argparse
import os.path
import sys
from pathlib import Path

from signers.SigThief import SigThief
from utils.console import Console

if __name__ == "__main__":
    os.system('color')
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--file", dest="inputfile", type=str, required=True,
                        help="input file or directory (check)", metavar="FILE")
    parser.add_argument('-a', '--action', dest='action', choices=SigThief.ACTIONS, required=True,
                        help='Action to perform on input file')
    parser.add_argument('-o', '--output', dest='outputfile', type=str, required=False,
                        help='Store result in output file')
    parser.add_argument('-s', '--sig', dest='sigfile', type=str, required=False,
                        help='binary signature from disk')
    args = parser.parse_args()

    certificate_file = None
    if args.sigfile:
        certificate_file = args.sigfile

    sig_thief = SigThief(action=args.action, certificate_file=certificate_file)

    if args.action == "save":
        sig_thief.save_cert(args.inputfile)

    elif args.action == "clone":
        if not (args.outputfile and os.path.isfile(args.outputfile)):
            raise FileNotFoundError(f"[-] File {args.outputfile} not found")
        sig_thief.sign(args.inputfile, args.outputfile)

    elif args.action == "check":
        if os.path.isfile(args.inputfile):
            sig_thief.check_sig(args.inputfile)
        elif os.path.isdir(args.inputfile):
            directory = Path(args.inputfile).absolute()
            for file in os.listdir(directory):
                print(f"[*] {file}: ", end='')
                absolute_path = directory.joinpath(file)
                if os.path.isfile(absolute_path) and os.path.splitext(file)[1].lower() in [".dll", ".exe"]:
                    if sig_thief.check_sig(absolute_path, echo=False):
                        Console.success_line("Signed")
                    else:
                        Console.fail_line("Not signed")
                else:
                    Console.info_line("Skipped")
        else:
            print("[-] Wrong path")
            exit(1)

    elif args.action == "add":
        if not certificate_file or not os.path.isfile(certificate_file):
            Console.auto_line("[-] Certificate file not provided or not found")
            sys.exit(1)
        if not (args.inputfile and os.path.isfile(args.inputfile)):
            raise FileNotFoundError(f"[-] File {args.inputfile} not found")
        if not (args.outputfile and os.path.isfile(args.outputfile)):
            raise FileNotFoundError(f"[-] File {args.outputfile} not found")

        sig_thief.sign_with(signee=args.inputfile, signed=args.outputfile, certificate=certificate_file)

    elif args.action == "del":
        if not (args.inputfile and os.path.isfile(args.inputfile)):
            raise FileNotFoundError(f"[-] File {args.inputfile} not found")
        sig_thief.truncate(args.inputfile, args.outputfile)
    else:
        parser.print_help()
