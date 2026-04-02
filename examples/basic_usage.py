"""Basic usage examples for verilog_parser."""

from verilog_parser import VerilogParser, format_cell

# --- 1. Parse a file ---
parser = VerilogParser()
verilog = parser.read("../tests/sample.v")

print(repr(verilog))
# Verilog(cells=4, files=1)

# --- 2. List all cells ---
print(list(verilog.cells.keys()))
# ['INV_X1', 'AND2_X1', 'DFFS_X2', 'TBUF_X1']

# --- 3. Get all pins for a cell (non-mixed mode by default) ---
print(verilog.get_pins("INV_X1"))
# ['A', 'ZN']

# --- 4. Get pins for mixed mode ---
print(verilog.get_pins("INV_X1", mode="mixed"))
# ['A', 'ZN']

# --- 5. Get pin directions ---
print(verilog.get_pin_directions("INV_X1"))
# {'input': ['A'], 'output': ['ZN'], 'inout': []}

print(verilog.get_pin_directions("INV_X1", mode="mixed"))
# {'input': ['A'], 'output': [], 'inout': ['ZN']}

# --- 6. Pretty-print a full cell (both modes) ---
print(format_cell(verilog.cells["DFFS_X2"]))
# [mixed]
#     pins:   D, CK, SN, Q, QN
#     input:  D, CK, SN
#     inout:  Q, QN
# [non-mixed]
#     pins:   D, CK, SN, Q, QN
#     input:  D, CK, SN
#     output: Q, QN

# --- 7. Reuse the parser for a second file ---
parser.reset()
verilog2 = parser.read("../tests/sample.v")
print(verilog2.cells.keys())
