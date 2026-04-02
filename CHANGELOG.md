# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-04-02

### Added
- Initial release.
- `VerilogParser.read()` — parse a `.v` cell-library file into a `Verilog` result object.
- `VerilogParser.reset()` — clear state for parser reuse.
- `Verilog.get_pins()` — return pin list for a cell in a given mode.
- `Verilog.get_pin_directions()` — return direction → pin mapping for a cell in a given mode.
- Support for `mixed` and `non-mixed` modes via `` `ifdef MIXEDMODE `` blocks.
- `format_cell()` utility for human-readable pin output.
- CLI via `verilog-parser` / `python -m verilog_parser`.
- Optional colored warnings with `termcolor` (graceful fallback if not installed).
- MIT license.
