/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_sync.v
// @author        3book
// @description   
// @created       2019-11-15T22:05:26.452Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:19:31.289Z+08:00
*******************************************************************************/

`timescale 1ns/100ps
module args_sync #(
parameter N = 10   ,//Number of sync
parameter [N-1:0]   INIT = 0 //INIT value
)(
input   c,//clock
input   i,//input data
output  o //output data
);
wire [N:0] ii;
assign ii[0] = i;
genvar j;
generate
    for (j = 0; j<N; j=j+1) begin:SYNC_REG
    (* shreg_extract = "no", ASYNC_REG = "TRUE" *)
    FD #(
    .INIT (INIT[j])
    ) sync_reg (
    .C  (c),
    .D  (ii[j]),
    .Q  (ii[j+1])
    );
end
endgenerate
assign o = ii[N];
endmodule
