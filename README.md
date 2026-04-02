# verilog-parser

A pure-Python parser for **Verilog cell-library** (`.v`) files — used in EDA
flows to describe the pins and port directions of standard cells.

[![CI](https://github.com/rohaansch/verilog-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/rohaansch/eda-verilog-parser/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://pypi.org/project/eda-verilog-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Related article

[Building a Python Verilog Cell Library Parser for EDA Automation](https://medium.com/@rohanchadhury/building-a-python-verilog-cell-library-parser-for-eda-automation-9a6af3e8f17c)
— A walkthrough of the design decisions and real-world use cases behind this library.

## Features

- Parses `` `celldefine `` / `` `endcelldefine `` blocks with `module`, `input`,
  `output`, and `inout` declarations
- Supports **mixed** and **non-mixed** mode variants via `` `ifdef MIXEDMODE ``
- **Zero required dependencies** — only the Python standard library
- Optional colored warnings via [`termcolor`](https://pypi.org/project/termcolor/)
- CLI included: `verilog-parser cells.v --cell INV_X1`

## Installation

```bash
pip install eda-verilog-parser                  # no extra dependencies
pip install "eda-verilog-parser[color]"         # adds termcolor for colored warnings
```

Or for development:

```bash
git clone https://github.com/rohaansch/verilog-parser
cd verilog-parser
pip install -e ".[dev]"
```

## Quick start

```python
from verilog_parser import VerilogParser

parser = VerilogParser()
verilog = parser.read("cells.v")

print(repr(verilog))
# Verilog(cells=4, files=1)

print(verilog.get_pins("INV_X1"))
# ['A', 'ZN']

print(verilog.get_pin_directions("INV_X1"))
# {'input': ['A'], 'output': ['ZN'], 'inout': []}

print(verilog.get_pin_directions("INV_X1", mode="mixed"))
# {'input': ['A'], 'output': [], 'inout': ['ZN']}
```

## Supported Verilog structure

The parser recognises cells defined with `` `celldefine `` / `` `endcelldefine ``
and `` `ifdef MIXEDMODE `` / `` `else `` / `` `endif `` sections:

```verilog
`celldefine
`ifdef MIXEDMODE
module INV_X1 (A, ZN);
  input A;
  inout ZN;
`else
module INV_X1 (A, ZN);
  input A;
  output ZN;
`endif
`endcelldefine
```

## Modes

| Mode | When used |
|---|---|
| `"non-mixed"` (default) | Digital-only simulation; outputs declared as `output` |
| `"mixed"` | Mixed-signal simulation; outputs declared as `inout` |

## API reference

### `VerilogParser(path=None)`

Create a parser. `path` sets the default file used by `read()`.

### `VerilogParser.read(path=None) → Verilog`

| Argument | Type | Description |
|---|---|---|
| `path` | `str` | `.v` file path. Falls back to the constructor path. |

Raises `ValueError` / `FileNotFoundError` / `IOError` on bad input.

### `VerilogParser.reset()`

Clear internal state to reuse the parser for a different file:

```python
v_fast = parser.read("lib_fast.v")
parser.reset()
v_slow = parser.read("lib_slow.v")
```

### `Verilog` object

| Attribute | Type | Description |
|---|---|---|
| `header` | `str` | Leading comment block from the parsed file |
| `cells` | `dict[str, dict]` | Cell name → mode → pin data |
| `files` | `list[str]` | Absolute paths of files contributing to this object |

### `Verilog.get_pins(cell_name, mode="non-mixed") → list[str]`

Return the ordered list of all pins for the given cell and mode.

### `Verilog.get_pin_directions(cell_name, mode="non-mixed") → dict`

Return a mapping of `"input"` / `"output"` / `"inout"` → pin list.

### `format_cell(cell) → str`

Format a cell's mode data as a human-readable multi-line string:

```python
from verilog_parser import format_cell
print(format_cell(verilog.cells["DFFS_X2"]))
# [mixed]
#     pins:   D, CK, SN, Q, QN
#     input:  D, CK, SN
#     inout:  Q, QN
# [non-mixed]
#     pins:   D, CK, SN, Q, QN
#     input:  D, CK, SN
#     output: Q, QN
```

## Command-line usage

```
verilog-parser cells.v
verilog-parser cells.v --cell INV_X1
verilog-parser cells.v --cell INV_X1 --mode mixed
verilog-parser cells.v --header
verilog-parser --version
```

Or without installing:

```
python -m verilog_parser cells.v --cell INV_X1
```

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

## License

[MIT](LICENSE)
