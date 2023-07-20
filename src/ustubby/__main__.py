import argparse
import importlib
import sys
from pathlib import Path

import ustubby


def main() -> int:
    parser = argparse.ArgumentParser(description="Converts a python file into micropython c extension stubs.")
    parser.add_argument("input", type=Path,
                        help="Python file to convert.")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output C file. Defaults to \"${input}.c\".")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite output file if it already exists.")
    args = parser.parse_args()

    ########################################
    # Preprocess and error-check arguments #
    ########################################
    if not args.input.exists():
        print(f"{args.input} does not exist.")
        return 1

    if args.input.suffix != ".py":
        print(f"{args.input} is not a \".py\" file.")
        return 1

    args.input = args.input.expanduser().resolve()

    if args.output is None:
        args.output = args.input.with_suffix(".c")

    if args.output.suffix != ".c":
        print(f"{args.output} is not a \".c\" file.")
        return 1

    if args.output.exists() and not args.overwrite:
        print(f"{args.output} already exists.")
        return 1

    ###################
    # Execute ustubby #
    ###################
    sys.path.insert(0, str(args.input.parent))

    module = importlib.import_module(args.input.stem)

    c_output = ustubby.stub_module(module)

    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(c_output)

    return 0

if __name__ == "__main__":
    sys.exit(main())
