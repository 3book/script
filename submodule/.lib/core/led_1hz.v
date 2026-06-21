/********************************************************************************
// @project       Audio Bridge Unit(Breakout box)
// @filename      clk_rst.v
// @author        xuyapeng
// @description   
// @copyright     Copyright (c)  Beacon Display Technology Co.,Ltd
// @created       2021-06-28T10:35:08.612Z+08:00
// @last-modified 2021-07-07T19:19:25.381Z+08:00
*******************************************************************************/
`timescale 1ns/10ps
module led_1hz #(
    parameter CLK_FREQ = 100    ,//frequence MHz
    parameter LED_FREQ = 1      ,//frequence Hz
    parameter REG_DW   = 32      //register data width
    )(
    input  rstin,
    inout  clkin,
    output led_1hz,
    input  [REG_DW-1:0] reg_cfg//
);


//generate 1Hz for LED
localparam LED_LSB = $clog2(CLK_FREQ*1000000/LED_FREQ/2);
reg [LED_LSB:0] led_cnt = 'h0 ;

always @(posedge clkin) begin
    led_cnt <= led_cnt + 1'b1;
end
assign led_1hz = led_cnt[LED_LSB];  //for hardware

endmodule