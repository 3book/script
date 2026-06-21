/********************************************************************************
// @project       
// @filename      freq_chk.v
// @author        3book
// @description   
// @copyright     Copyright (c)  
// @created       2024-12-23T23:15:23.300Z+08:00
// @last-modified 2024-12-23T23:49:59.790Z+08:00
*******************************************************************************/
`timescale 1ns/10ps
module freq_chk #(
    parameter CLK_FREQ = 1000000,//clock frequence Hz
    parameter CHK_FREQ = 100    ,//check frequence Hz
    parameter CHK_TIME = 5      ,//check times
    parameter LED_FREQ = 1      ,//frequence Hz
    parameter REG_DW   = 32      //register data width
    )(
    inout  clk,
    input  rst,
    input  in,
    output led_1hz,
    input  [REG_DW-1:0] reg_cfg//
);
localparam MAX_A = CLK_FREQ/CHK_FREQ/2;
localparam AW = $clog2(MAX_A);
localparam MAX_B = CLK_FREQ/CHK_FREQ/2*CHK_TIME;
localparam BW = $clog2(MAX_B);
wire edge_i;
wire edge_rise;
wire edge_fall;
assign edge_i = in;
args_edge #(
    .EDGE   ("rise")
)args_edge_rise(
    .c  (clk),
    .r  (1'b0),
    .i  (edge_i),
    .o  (edge_rise)
    );
args_edge #(
    .EDGE   ("fall")
)args_edge_fall(
    .c  (clk),
    .r  (1'b0),
    .i  (edge_i),
    .o  (edge_fall)
    );
reg [AW-1:0] cnt_a;
always @(posedge clk) begin
    if((edge_rise==1'b1)||(edge_fall==1'b1))begin
        cnt_a <= 'b0;
    end else if(cnt_a!=MAX_A)begin
        cnt_a <= cnt_a + 1'b1;
    end else;
end
reg [BW-1:0] cnt_b;
always @(posedge clk) begin
    if(cnt_b!=MAX_B)begin

    if(cnt_a==MAX_A)begin
        cnt_b <= cnt_b + 1'b1;
    end else begin
        cnt_b <= 'b0;
    end
end

//generate 1Hz for LED
localparam LED_LSB = $clog2(CLK_FREQ*1000000/LED_FREQ/2);
reg [LED_LSB:0] led_cnt = 'h0 ;

always @(posedge clkin) begin
    led_cnt <= led_cnt + 1'b1;
end
assign led_1hz = led_cnt[LED_LSB];  //for hardware

endmodule