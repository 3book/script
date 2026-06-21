/********************************************************************************
// @project       VERILOG BASE
// @filename      args_edge.v
// @author        3book
// @description   plus algorithm
// @created       2019-07-17T14:36:12.125Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2021-07-18T00:02:46.717Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
// variable number of arguments
// latency=$clog2(N)+1
module args_divider #(
    parameter DIVIDER_FACTOR = 2 //divider factor must greater 1
)(
input   c,
input   r,
// input   i
output  o
);
localparam W = $clog2(DIVIDER_FACTOR);
wire flag;
reg [W-1:0] div_cnt = {W{1'b0}};
reg o_r = 1'b0;

// always @(posedge c ) begin
//     i_r <= i;
// end
assign flag=div_cnt==DIVIDER_FACTOR/2-1;
always @(posedge c) begin
    if (r==1'b1) begin
        div_cnt <= {W{1'b0}};
    end else if (flag==1'b1) begin
        div_cnt <= {W{1'b0}};
    end else begin
        div_cnt <= div_cnt+1;
    end
end
always @(posedge c) begin
    if (flag==1'b1) begin
        o_r <= ~o_r;
    end
end
assign o = o_r;
endmodule