"""Tests for verilog_parser."""

import os
import pytest

from verilog_parser import VerilogParser, Verilog, format_cell

SAMPLE_V = os.path.join(os.path.dirname(__file__), "sample.v")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def verilog():
    return VerilogParser().read(SAMPLE_V)


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------

class TestBasicParsing:
    def test_returns_verilog_instance(self, verilog):
        assert isinstance(verilog, Verilog)

    def test_all_cells_present(self, verilog):
        assert set(verilog.cells.keys()) == {"INV_X1", "AND2_X1", "DFFS_X2", "TBUF_X1"}

    def test_files_populated(self, verilog):
        assert len(verilog.files) == 1
        assert verilog.files[0].endswith("sample.v")

    def test_repr(self, verilog):
        r = repr(verilog)
        assert "cells=4" in r
        assert "files=1" in r


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

class TestHeader:
    def test_header_is_string(self, verilog):
        assert isinstance(verilog.header, str)

    def test_header_nonempty(self, verilog):
        assert len(verilog.header) > 0

    def test_header_contains_lib_name(self, verilog):
        assert "sample_lib" in verilog.header


# ---------------------------------------------------------------------------
# INV_X1 — simple inverter
# ---------------------------------------------------------------------------

class TestINV:
    def test_non_mixed_pins(self, verilog):
        pins = verilog.get_pins("INV_X1", mode="non-mixed")
        assert pins == ["A", "ZN"]

    def test_mixed_pins(self, verilog):
        pins = verilog.get_pins("INV_X1", mode="mixed")
        assert pins == ["A", "ZN"]

    def test_non_mixed_directions(self, verilog):
        dirs = verilog.get_pin_directions("INV_X1", mode="non-mixed")
        assert dirs["input"] == ["A"]
        assert dirs["output"] == ["ZN"]
        assert dirs["inout"] == []

    def test_mixed_directions(self, verilog):
        dirs = verilog.get_pin_directions("INV_X1", mode="mixed")
        assert dirs["input"] == ["A"]
        assert dirs["inout"] == ["ZN"]
        assert dirs["output"] == []

    def test_default_mode_is_non_mixed(self, verilog):
        assert verilog.get_pins("INV_X1") == verilog.get_pins("INV_X1", mode="non-mixed")


# ---------------------------------------------------------------------------
# AND2_X1 — 2-input AND gate
# ---------------------------------------------------------------------------

class TestAND2:
    def test_pins(self, verilog):
        assert verilog.get_pins("AND2_X1") == ["A1", "A2", "Z"]

    def test_input_pins(self, verilog):
        dirs = verilog.get_pin_directions("AND2_X1")
        assert dirs["input"] == ["A1", "A2"]

    def test_output_pin(self, verilog):
        dirs = verilog.get_pin_directions("AND2_X1")
        assert dirs["output"] == ["Z"]


# ---------------------------------------------------------------------------
# DFFS_X2 — D flip-flop with set (multiple inputs/outputs)
# ---------------------------------------------------------------------------

class TestDFFS:
    def test_pins(self, verilog):
        assert verilog.get_pins("DFFS_X2") == ["D", "CK", "SN", "Q", "QN"]

    def test_non_mixed_inputs(self, verilog):
        dirs = verilog.get_pin_directions("DFFS_X2", mode="non-mixed")
        assert dirs["input"] == ["D", "CK", "SN"]

    def test_non_mixed_outputs(self, verilog):
        dirs = verilog.get_pin_directions("DFFS_X2", mode="non-mixed")
        assert dirs["output"] == ["Q", "QN"]

    def test_mixed_inout(self, verilog):
        dirs = verilog.get_pin_directions("DFFS_X2", mode="mixed")
        assert dirs["inout"] == ["Q", "QN"]
        assert dirs["output"] == []


# ---------------------------------------------------------------------------
# TBUF_X1 — tri-state buffer
# ---------------------------------------------------------------------------

class TestTBUF:
    def test_pins(self, verilog):
        assert verilog.get_pins("TBUF_X1") == ["A", "OE", "Z"]

    def test_non_mixed_output(self, verilog):
        dirs = verilog.get_pin_directions("TBUF_X1")
        assert dirs["output"] == ["Z"]

    def test_mixed_inout(self, verilog):
        dirs = verilog.get_pin_directions("TBUF_X1", mode="mixed")
        assert dirs["inout"] == ["Z"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_no_path_raises(self):
        with pytest.raises(ValueError, match="not provided"):
            VerilogParser().read()

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            VerilogParser().read("/nonexistent/path/cells.v")

    def test_missing_cell_raises(self, verilog):
        with pytest.raises(KeyError, match="not found"):
            verilog.get_pins("NONEXISTENT_CELL")

    def test_missing_mode_raises(self, verilog):
        with pytest.raises(KeyError, match="not found"):
            verilog.get_pins("INV_X1", mode="invalid-mode")


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_clears_state(self):
        parser = VerilogParser()
        parser.read(SAMPLE_V)
        assert parser.verilog is not None

        parser.reset()
        assert parser.verilog is None

    def test_reuse_after_reset(self):
        parser = VerilogParser()
        v_a = parser.read(SAMPLE_V)

        parser.reset()
        v_b = parser.read(SAMPLE_V)

        assert v_a.cells.keys() == v_b.cells.keys()


# ---------------------------------------------------------------------------
# format_cell utility
# ---------------------------------------------------------------------------

class TestFormatCell:
    def test_output_is_string(self, verilog):
        result = format_cell(verilog.cells["INV_X1"])
        assert isinstance(result, str)

    def test_contains_mode_label(self, verilog):
        result = format_cell(verilog.cells["INV_X1"])
        assert "non-mixed" in result
        assert "mixed" in result

    def test_contains_pin_names(self, verilog):
        result = format_cell(verilog.cells["INV_X1"])
        assert "A" in result
        assert "ZN" in result

    def test_single_mode(self, verilog):
        single = {"non-mixed": verilog.cells["INV_X1"]["non-mixed"]}
        result = format_cell(single)
        assert "[non-mixed]" in result
        assert "[mixed]" not in result
