/********************************************************************************
// @project       VERILOG BASE
// @filename      args_edge.v
// @author        3book
// @description   plus algorithm
// @created       2019-07-17T14:36:12.125Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2021-07-18T01:03:33.557Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
// variable number of arguments
// latency=$clog2(N)+1
module args_edge #(
    parameter EDGE = "rise",//argument EDGE, rise or fall or all
    parameter N = 9     //argument Number
)(
input   c,
input   r,
input   i,
output  o
);
reg i_r = 1'b0;
reg o_r = 1'b0;
always @(posedge c ) begin
    i_r <= i;
end
generate
    if ((EDGE == "rise")||(EDGE == "ALL")) begin
        always @(posedge c ) begin
            if(r==1'b1)begin
                o_r <= 1'b0;
            end else if(i&&!i_r)begin
                o_r <= 1'b1;
            end else begin
                o_r <= 1'b0;
            end
        end
    end
    if ((EDGE == "fall")||(EDGE == "ALL")) begin
        always @(posedge c ) begin
            if(r==1'b1)begin
                o_r <= 1'b0;
            end else if(!i&&i_r)begin
                o_r <= 1'b1;
            end else begin
                o_r <= 1'b0;
            end
        end
    end
endgenerate
assign o = o_r;
endmodule