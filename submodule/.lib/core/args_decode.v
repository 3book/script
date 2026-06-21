/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_decode.v
// @author        3book
// @description   
// @created       2019-11-06T18:14:10.430Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:18:44.718Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
module args_decode #(                           
parameter N = 2    //in data width 
)(
input          clk,
input          rst,
input [N-1:0]  c  , //channel number
output[2**N-1:0] s  //channel select
);
// wire [N-1:0]    m [2**N-1:0];
genvar i;
generate
    for (i=0;i<2**N;i=i+1) begin
        // assign m[i] = i; 
        localparam [N-1:0] M=i;
        assign s[i] = (c==M) ? 1'b1:1'b0; 
    end
endgenerate

// SRLC32E #(
//     .INIT(32'h00000000) // Initial Value of Shift Register
// ) SRLC32E_inst (
//     .Q(Q),     // SRL data output
//     .Q31(Q31), // SRL cascade output pin
//     .A(A),     // 5-bit shift depth select input
//     .CE(CE),   // Clock enable input
//     .CLK(CLK), // Clock input
//     .D(D)      // SRL data input
// );

// SRL16E #(
//       .INIT(16'h0000) // Initial Value of Shift Register
//    ) SRL16E_inst (
//       .Q(Q),       // SRL data output
//       .A0(A0),     // Select[0] input
//       .A1(A1),     // Select[1] input
//       .A2(A2),     // Select[2] input
//       .A3(A3),     // Select[3] input
//       .CE(CE),     // Clock enable input
//       .CLK(CLK),   // Clock input
//       .D(D)        // SRL data input
//    );
endmodule