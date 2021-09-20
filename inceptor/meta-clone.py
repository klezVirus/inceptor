import argparse
import os

from utils.MetaTwin import MetaTwin

if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(description="Simple Metadata Cloner")
    parser.add_argument("-s", "--source", type=str, required=True, help="Copy metadata from this binary")
    parser.add_argument("-d", "--destination", type=str, required=True, help="Copy metadata to this binary")
    parser.add_argument("-w", "--view", action="store_true", required=False, help="Print binary metadata")
    args = parser.parse_args()

    cloner = MetaTwin()
    cloner.clone(copy_from=args.source, copy_to=args.destination)
    if args.view:
        if args.source and os.path.isfile(args.source):
            cloner.inspect(args.source)
        if args.destination and os.path.isfile(args.destination):
            cloner.inspect(args.destination)
