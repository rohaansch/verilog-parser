"""Core Verilog cell-library parser."""

from __future__ import annotations

import os
from collections import OrderedDict
from typing import Dict, List, Optional

from .utils import warning


class Verilog:
    """Result object returned by ``VerilogParser.read()``.

    Attributes:
        header: Comment block at the top of the parsed file.
        cells:  Mapping of cell name → mode → pin data.
                Each mode entry is a dict with keys ``pins``, ``input``,
                ``output``, and ``inout``.
        files:  Absolute paths of all files that contributed to this object.
    """

    def __init__(self) -> None:
        self.header: str = ""
        self.cells: Dict[str, Dict[str, dict]] = OrderedDict()
        self.files: List[str] = []

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Verilog(cells={len(self.cells)}, files={len(self.files)})"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_pins(self, cell_name: str, mode: str = "non-mixed") -> List[str]:
        """Return the ordered list of all pins for *cell_name* in *mode*.

        Args:
            cell_name: Exact cell name as it appears in the Verilog file.
            mode: ``"non-mixed"`` (default) or ``"mixed"``.

        Returns:
            List of pin-name strings in declaration order.

        Raises:
            KeyError: If *cell_name* or *mode* is not present.
        """
        self._check_cell(cell_name, mode)
        return self.cells[cell_name][mode]["pins"]

    def get_pin_directions(
        self, cell_name: str, mode: str = "non-mixed"
    ) -> Dict[str, List[str]]:
        """Return a mapping of direction → pin list for *cell_name* in *mode*.

        Args:
            cell_name: Exact cell name as it appears in the Verilog file.
            mode: ``"non-mixed"`` (default) or ``"mixed"``.

        Returns:
            Dict with keys ``"input"``, ``"output"``, ``"inout"`` (empty lists
            when a direction has no pins).

        Raises:
            KeyError: If *cell_name* or *mode* is not present.
        """
        self._check_cell(cell_name, mode)
        mode_dict = self.cells[cell_name][mode]
        return {k: v for k, v in mode_dict.items() if k != "pins"}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_cell(self, cell_name: str, mode: str) -> None:
        if cell_name not in self.cells:
            raise KeyError(
                f"Cell '{cell_name}' not found. "
                f"Available: {list(self.cells.keys())}"
            )
        if mode not in self.cells[cell_name]:
            raise KeyError(
                f"Mode '{mode}' not found for cell '{cell_name}'. "
                f"Available: {list(self.cells[cell_name].keys())}"
            )


class VerilogParser:
    """Parser for Verilog cell-library (`.v`) files.

    Usage::

        parser = VerilogParser()
        verilog = parser.read("cells.v")
        print(verilog.get_pins("INV_X1"))
        # ['A', 'ZN']

    Or pass the path at construction time::

        verilog = VerilogParser("cells.v").read()
    """

    def __init__(self, path: Optional[str] = None) -> None:
        self._default_path = path
        self.verilog: Optional[Verilog] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(self, path: Optional[str] = None) -> Verilog:
        """Parse a Verilog file and return a :class:`Verilog` result object.

        Args:
            path: Path to a ``.v`` file.  Falls back to the path supplied at
                  construction time.

        Returns:
            A :class:`Verilog` instance with ``header``, ``cells``, and
            ``files`` populated.

        Raises:
            ValueError: If no path was provided.
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be opened.
        """
        path = path or self._default_path
        if not path:
            raise ValueError(
                "Path not provided. "
                "Use VerilogParser(path) or VerilogParser().read(path)."
            )
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        verilog = Verilog()
        verilog.files.append(os.path.abspath(path))

        try:
            with open(path, "r") as fh:
                lines = fh.readlines()
        except IOError as exc:
            raise IOError(f"Could not read file: {path}") from exc

        state: Optional[str] = None  # None | "cell"
        mode: Optional[str] = None   # None | "mixed" | "non-mixed"
        cell_name: Optional[str] = None
        header_done = False

        for raw_line in lines:
            # Collect leading comment block as the file header
            if not header_done:
                if raw_line.startswith("//"):
                    verilog.header += raw_line
                    continue
                else:
                    header_done = True

            line = raw_line.strip()
            if not line:
                continue

            # ---- inside a `celldefine … `endif block ----
            if state == "cell":
                data = line.rstrip(";").split()

                if line == "`endif":
                    state = None
                    mode = None
                    cell_name = None

                elif line == "`ifdef MIXEDMODE":
                    mode = "mixed"

                elif line == "`else":
                    mode = "non-mixed"

                elif data[0] == "module" and mode is not None:
                    cell_name = data[1]
                    # Extract pins from the full parenthesised list (handles spaces after commas)
                    rest = line.rstrip(";")
                    paren_start = rest.find("(")
                    paren_end = rest.rfind(")")
                    if paren_start != -1 and paren_end != -1:
                        pins_str = rest[paren_start + 1 : paren_end]
                    else:
                        pins_str = ""
                    pins = [p.strip() for p in pins_str.split(",") if p.strip()]
                    verilog.cells.setdefault(cell_name, {})
                    verilog.cells[cell_name][mode] = {
                        "pins": pins,
                        "input": [],
                        "output": [],
                        "inout": [],
                    }

                elif (
                    data[0] in {"input", "output", "inout"}
                    and cell_name is not None
                    and mode is not None
                ):
                    pin_list = [p for p in data[1].split(",") if p] if len(data) > 1 else []
                    verilog.cells[cell_name][mode][data[0]] = pin_list

                elif line not in {"`endcelldefine", "endmodule"}:
                    warning(f"Unrecognized line in cell block: {line!r}")

            # ---- trigger: enter cell block ----
            if line == "`celldefine":
                state = "cell"

        self.verilog = verilog
        return verilog

    def reset(self) -> None:
        """Clear internal state so the parser can be reused for a new file.

        Example::

            parser = VerilogParser()
            verilog_a = parser.read("lib_a.v")
            parser.reset()
            verilog_b = parser.read("lib_b.v")
        """
        self.verilog = None
