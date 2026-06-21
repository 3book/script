/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_binary.v
// @author        3book
// @description   Binary process
// @created       2019-07-26T11:44:59.547Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:18:17.813Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
module args_binary #(                           
parameter IW = 10   ,//in data width 
parameter OW = 1     //out data width
)(
input           clk,
input           rst,
input [IW-1:0]  in,//in data    
output[OW-1:0]  out,//out data    
//register
input  [IW-1:0]   cfg_threshold
);
reg [OW-1:0]  do_r;
always @(posedge clk ) begin
    if(in>=cfg_threshold)begin
        do_r <= {OW{1'b1}};
    end else begin
        do_r <= {OW{1'b0}};
    end
end
assign out = do_r;
endmodule