"""CLI entry point: python -m verilog_parser  or  verilog-parser (installed script)."""

import argparse
import sys

from .parser import VerilogParser
from .utils import format_cell


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="verilog-parser",
        description="Parse a Verilog cell-library file and print pin data.",
        epilog=(
            "Examples:\n"
            "  verilog-parser cells.v\n"
            "  verilog-parser cells.v --cell INV_X1\n"
            "  verilog-parser cells.v --cell INV_X1 --mode mixed\n"
            "  verilog-parser cells.v --header\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="Path to a .v Verilog cell-library file")
    parser.add_argument(
        "--cell", "-c",
        metavar="CELLNAME",
        help="Print only this cell (case-insensitive)",
    )
    parser.add_argument(
        "--mode", "-m",
        metavar="MODE",
        default=None,
        help="Pin mode to display: 'mixed' or 'non-mixed' (default: show all modes)",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Print the file header comment block",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print package version and exit",
    )
    args = parser.parse_args()

    if args.version:
        from verilog_parser import __version__
        print(__version__)
        return

    try:
        verilog = VerilogParser().read(args.path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.header:
        print("=== Header ===")
        print(verilog.header.strip() if verilog.header else "(no header)")
        print()

    if args.cell:
        cell_key = next(
            (k for k in verilog.cells if k.lower() == args.cell.lower()), None
        )
        if not cell_key:
            print(f"Cell '{args.cell}' not found.", file=sys.stderr)
            sys.exit(1)

        print(f"=== {cell_key} ===")
        cell_data = verilog.cells[cell_key]

        if args.mode:
            if args.mode not in cell_data:
                print(
                    f"Mode '{args.mode}' not found for cell '{cell_key}'. "
                    f"Available: {list(cell_data.keys())}",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(format_cell({args.mode: cell_data[args.mode]}))
        else:
            print(format_cell(cell_data))
    else:
        for cell_name, cell_data in verilog.cells.items():
            modes = list(cell_data.keys())
            print(f"=== {cell_name} ({', '.join(modes)}) ===")
            print(format_cell(cell_data))
            print()


if __name__ == "__main__":
    main()
