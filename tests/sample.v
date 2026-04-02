// Verilog Cell Library: sample_lib
// Technology: sample_tech
// Version: 1.0
// Description: Sample cell definitions for verilog_parser tests

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

`celldefine
`ifdef MIXEDMODE
module AND2_X1 (A1, A2, Z);
  input A1,A2;
  inout Z;
`else
module AND2_X1 (A1, A2, Z);
  input A1,A2;
  output Z;
`endif
`endcelldefine

`celldefine
`ifdef MIXEDMODE
module DFFS_X2 (D, CK, SN, Q, QN);
  input D,CK,SN;
  inout Q,QN;
`else
module DFFS_X2 (D, CK, SN, Q, QN);
  input D,CK,SN;
  output Q,QN;
`endif
`endcelldefine

`celldefine
`ifdef MIXEDMODE
module TBUF_X1 (A, OE, Z);
  input A,OE;
  inout Z;
`else
module TBUF_X1 (A, OE, Z);
  input A,OE;
  output Z;
`endif
`endcelldefine
