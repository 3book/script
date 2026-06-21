/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_mux.v
// @author        3book
// @description   
// @created       2020-03-23T08:17:09.354Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:19:09.436Z+08:00
*******************************************************************************/

// latency=1
`timescale 1ns/100ps
module args_mux #(
parameter W = 10,   //argument Data Width
parameter N = 4     //argument Number
)(
input               clk,
input               rst,
input   [$clog2(N)-1:0]   sel,
input   [W*N-1:0]   in,
output  [W-1:0]   out
);
reg [W-1:0]   s_out; 
integer	 i;
// always @(*) begin
always @(posedge clk) begin
    if ( rst == 1'b1 )begin
        s_out <= 'b0;
    end else begin
            s_out <= in[sel*W+:W];
        // for ( i = 0; i < N; i = i+1 )begin
        //     if( sel == i )begin
        //     end else begin
        //         s_out <= in[i*0+:W];
            // end
        // end
    end
end
assign out=s_out;
// args_delay #(
// .WIDTH  (W      ),
// .DELAY  (1      )
// )args_delay_inst(
// .clk    (clk    ),//clock
// .in     (s_out  ),
// .out    (out    )
// );

endmodule