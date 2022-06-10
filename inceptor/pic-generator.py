import argparse

import utils.utils
from converters.TextExtract import TextExtract

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Text Extractor Test")
    parser.add_argument("target", help="C file to compile")
    parser.add_argument("-v", "--variable", required=False, default="shellcode", help="Variable name")
    args = parser.parse_args()

    t = TextExtract()
    raw = t.transform(target=args.target)
    print(utils.utils.format_shellcode(raw, variable=args.variable))

