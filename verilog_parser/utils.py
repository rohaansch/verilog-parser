"""Utility helpers for verilog_parser."""

from __future__ import annotations

from typing import Dict

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, **kwargs):  # type: ignore[misc]
        return text


def warning(message: str) -> None:
    """Print a yellow warning message (requires ``termcolor``; graceful fallback)."""
    print(colored(f"WARNING: {message}", "yellow"))


def format_cell(cell: Dict[str, dict]) -> str:
    """Format a cell's mode data as a human-readable multi-line string.

    Args:
        cell: Dict mapping mode name (``"mixed"`` / ``"non-mixed"``) to the
              pin-data dict (as stored in ``Verilog.cells[cell_name]``).

    Returns:
        Human-readable string, one section per mode.

    Example::

        from verilog_parser import VerilogParser, format_cell
        verilog = VerilogParser().read("cells.v")
        print(format_cell(verilog.cells["INV_X1"]))
    """
    lines = []
    for mode, data in cell.items():
        lines.append(f"  [{mode}]")
        lines.append(f"    pins:   {', '.join(data['pins'])}")
        for direction in ("input", "output", "inout"):
            if data[direction]:
                lines.append(f"    {direction}:  {', '.join(data[direction])}")
    return "\n".join(lines)
