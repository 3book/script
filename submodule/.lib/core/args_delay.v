/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_delay.v
// @author        3book
// @description   
// @created       2019-11-16T17:21:37.390Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:18:52.886Z+08:00
*******************************************************************************/

`timescale 1ns/100ps
module args_delay #(
parameter TYPE  = "DRAM",//ram type
parameter WIDTH = 2   ,//data width
parameter DELAY = 1    //Number of delay
)(
input               clk,//clock
input               rst,//reset
input   [WIDTH-1:0] in,//input data
output  [WIDTH-1:0] out//output data
);
genvar i;
generate
    if(TYPE=="DRAM")begin
        for (i = 0; i<WIDTH; i=i+1) begin:ARGS_SYNC
        args_sync #(
        .N      (DELAY      )
        )args_sync_inst0(
        .c      (clk    ),
        .i      (in[i]  ),
        .o      (out[i] )
        );
        end
    end

    if(TYPE=="BRAM")begin
    localparam DEPTH = (2**$clog2(DELAY)>512) ? 2**$clog2(DELAY) : 512;
    reg                   rden;
    reg  [$clog2(DEPTH)-1:0] raddr='b0;
    reg  [$clog2(DEPTH)-1:0] waddr='b0;
    always @(posedge clk ) begin
        if(rst==1'b1)begin
            waddr <= 'b0;
        end else begin
            waddr <= waddr + 1'b1;
        end
    end
    always @(posedge clk ) begin
        if(rst==1'b1)begin
            raddr <= 'b0;
        end else if(rden==1'b1) begin
            raddr <= raddr + 1'b1;
        end else;
    end
    always @(posedge clk ) begin
        if(rst==1'b1)begin
            rden <= 1'b0;
        end else if(waddr==DELAY-2)begin
            rden <= 1'b1;
        end else;
    end
    sync_bram_sdp #(
    .WIDTH                  (WIDTH                  ),
    .DEPTH                  (DEPTH                  ),
    .BRAM_SIZE              ("18Kb"                 ),
    .DEVICE                 ("7SERIES"              ),
    .DO_REG                 (0                      ),
    .INIT_FILE              ("NONE"                 ),
    .SIM_COLLISION_CHECK    ("ALL"                  ),
    .SRVAL                  (72'h000000000000000000 ),
    .INIT                   (72'h000000000000000000 ),
    .WRITE_MODE             ("WRITE_FIRST"          )
    )sync_bram_sdp_inst(
    .clk                    (clk                    ),
    .rst                    (rst                    ),
    .rddata                 (out                    ),
    .rdaddr                 (raddr                  ),
    .rden                   (rden                   ),
    .wren                   (1'b1                   ),
    .wraddr                 (waddr                  ),
    .wrdata                 (in                     )
    );
    end
endgenerate
endmodule