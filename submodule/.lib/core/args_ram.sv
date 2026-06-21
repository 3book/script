/********************************************************************************
// @project       
// @filename      args_ram.sv
// @author        3book
// @description   
// @copyright     Copyright (c)  
// @created       2023-06-30T09:30:59.732Z+08:00
// @last-modified 2026-03-15T22:09:30.824Z+08:00
*******************************************************************************/
`timescale 1ns / 1ps
module args_ram #(
    parameter AW0 = 11,  //address width
    parameter DW0 = 32,  //data width
    parameter AW1 = 10,  //address width
    parameter DW1 = 64   //data width
    // parameter QREG = 1    //
) (
    input   clk0,
    input   clk1,
    // input   rst,
    input   [AW0-1:0]    addr0,
    input   [DW0-1:0]    wdat0,
    output  [DW0-1:0]    rdat0,
    input   wren0,
    // input   r0,
    input   [AW1-1:0]    addr1,
    input   [DW1-1:0]    wdat1,
    output  [DW1-1:0]    rdat1,
    input   wren1
    // input   r1 
);

  // memory
  //   localparam XW = (DW0 < DW1) ? DW0 : DW1;  // X direct width
  localparam XW = DW0;  // X direct width
  localparam YW = 1 << AW0;  // Y direct width
  localparam RT = DW1 / DW0;
  localparam ZW = $clog2(RT);
  reg  [DW0-1:0] mem[YW];
  // mapping infterface
  wire [AW0-1:0] a0;
  wire [DW0-1:0] d0;
  reg  [DW0-1:0] q0='b0;
  wire           w0;
  wire [AW1-1:0] a1;
  wire [DW1-1:0] d1;
  reg  [DW1-1:0] q1='b0;
  wire           w1;
  //   if (QREG == 0) begin : gen_stage0
  //     wire [DW0-1:0] q0;
  //     wire [DW1-1:0] q1;
  //   end else begin : gen_stage1
  //   reg  [DW0-1:0] q0;
  //   reg  [DW1-1:0] q1;
  //   end
genvar i;
  initial begin
    for (int i = 0; i < YW; i = i + 1) begin
      mem[i] = 'b0;
    end
  end
  assign a0 = addr0;
  assign w0 = wren0;
  assign d0 = wdat0;
  assign rdat0 = q0;
  assign a1 = addr1;
  assign w1 = wren1;
  assign d1 = wdat1;
  assign rdat1 = q1;
  // portA
  always @(posedge clk0) begin
    if (w0 == 1'b1) begin
      mem[a0] <= d0[0+:DW0];
    end else;
    q0 <= mem[a0];
  end
  // portB
  always @(posedge clk1) begin
    if (RT == 1) begin
      if (w1 == 1'b1) begin
        mem[a1] <= d1[0*DW1+:DW1];
      end else;
      q1 <= mem[a1];
    end else begin
      
      for (int i = 0; i < RT; i = i + 1) begin
        reg [ZW-1:0] sub_a1;
        sub_a1=i;
        if (w1 == 1'b1) begin
          mem[{a1, sub_a1}] <= d1[i*DW0+:DW0];
        //   mem[{a1, i[0+:ZW]}] <= d1[i*DW0+:DW0];
        end else;
        q1[i*DW0+:DW0] <= mem[{a1, sub_a1}];
        // q1[i*DW0+:DW0] <= mem[{a1, i[0+:ZW]}];
      end
    end
  end
endmodule : args_ram
