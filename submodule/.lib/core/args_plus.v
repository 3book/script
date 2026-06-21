/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_plus.v
// @author        3book
// @description   plus algorithm
// @created       2019-07-17T14:36:12.125Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2019-07-26T16:08:38.146Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
// variable number of arguments
// latency=$clog2(N)+1
module args_plus #(
    parameter W = 10,   //argument Data Width
    parameter N = 9     //argument Number
)(
input               clk,
input               rst,
input   [W*N-1:0]   in,
output  [W+$clog2(N)-1:0] out
);
localparam WP = $clog2(N);  //width padding
localparam M = 2**WP;   //Number all
localparam WA = W+WP;   //Width all

reg  [WA*M*2-1:0] tmp = 'b0;

genvar i,j;
generate
    for (i = 0;i<N;i=i+1 ) begin:args_padding
        always @(posedge clk ) begin
            // tmp[WA*M+:WA*M] <= {{WA*(M-N){1'b0}},in};
            tmp[(i+M)*WA+:WA] <= {{WP{1'b0}},in[i*W+:W]};
        end
    end
    for (j = 0;j<WP;j=j+1 ) begin:args_plus
        localparam WT = WA*(2**(WP-j-1));
        always @(posedge clk ) begin
            tmp[WT+:WT] <= tmp[2*WT+:WT] +tmp[3*WT+:WT];
        end
    end
assign out = tmp[WA+:WA];
endgenerate
endmodule