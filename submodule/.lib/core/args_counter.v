/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_counter.v
// @author        3book
// @description   
// @created       2019-07-26T23:30:56.974Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2019-07-26T23:56:51.551Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
module args_counter #(
    parameter N = 2 ,//counter number
    parameter W = 32 //reguster data width
    )(
    input clk           ,//clock
    input clr           ,//clear
    input [N-1:0] plus ,//
    output [N*W-1:0] counters //output data
    ); 

    reg [N*W-1:0] cnts = {N*W{1'b0}};
    // reg [N*W-1:0] cnts;
genvar i;
generate
    for (i = 0; i<N; i = i+1) begin
        always @(posedge clk) begin
            if(clr==1'b1)begin
                cnts[i*W+:W] <= 'b0;
            end else if(plus[i]==1'b1) begin
                cnts[i*W+:W] <= cnts[i*W+:W] + 1'b1;
            end else;
        end
    end
endgenerate
assign counters = cnts;
endmodule
