/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_wconvert.v
// @author        3book
// @description   
// @created       2019-11-06T18:13:41.912Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:19:48.997Z+08:00
*******************************************************************************/

`timescale 1ns/100ps
module args_wconver#(                           
parameter IW = 10   ,//in data width 
parameter OW = 1     //out data width
)(
input           clk,
input           rst,
input [IW-1:0]  in,//in data    
output[OW-1:0]  out,//out data    
//register
input  [31:0]   cfg_threshold
);
reg [OW-1:0]  out_r;
always @(posedge clk ) begin
    if(in>=cfg_threshold)begin
        out_r <= {OW{1'b1}};
    end else begin
        out_r <= {OW{1'b0}};
    end
end
assign out = out_r;
endmodule