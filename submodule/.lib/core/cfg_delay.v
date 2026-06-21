/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_counter.v
// @author        3book
// @description   
// @created       2019-07-26T23:30:56.974Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2026-01-30T00:37:35.303Z+08:00
*******************************************************************************/
`timescale 1ns/100ps
module cfg_delay #(
    parameter MAX_DELAY = 1 ,//1s
    parameter W = 32 //reguster data width
    )(
    input clk           ,//clock
    input clr           ,
    input [15:0] reg_cfg,
    input in,//
    output out //output data
    );

reg in_1d;
reg in_2d;
reg in_3d;
always @(posedge clk) begin
    in_1d <= in;
    in_2d <= in_1d;
    in_3d <= in_2d;
end
wire rise;
wire fall;
assign rise=((in_2d==1'b1)&(in_3d==1'b0));
assign fall=((in_1d==1'b0)&(in_2d==1'b1));
reg [31:0] cnt_a={32{1'b1}};
reg [31:0] cnt_b={32{1'b1}};
always @(posedge clk) begin
    if(rise==1'b1)begin
        cnt_a <= 'b0;
    end else if(cnt_a=={32{1'b1}}) begin
        cnt_a <= cnt_a;
    end else begin
        cnt_a <= cnt_a +1'b1;
    end
end
always @(posedge clk) begin
    if(fall==1'b1)begin
        cnt_b <= 'b0;
    end else if(cnt_b=={32{1'b1}}) begin
        cnt_b <= cnt_b;
    end else begin
        cnt_b <= cnt_b +1'b1;
    end
end
wire reg_rise_dly_en;
wire reg_fall_dly_en;
wire [13:0] reg_dly;
assign reg_rise_dly_en=reg_cfg[15];
assign reg_fall_dly_en=reg_cfg[14];
assign reg_dly=reg_cfg[0+:14];

reg out_r=1'b0;
always @(posedge clk) begin
    if((reg_rise_dly_en==1'b0)&&(cnt_a==16'b0))begin
        out_r <= 1'b1;
    end else if((reg_rise_dly_en==1'b1)&&(cnt_a=={reg_dly,18'b0}))begin
        out_r <= 1'b1;
    end else if((reg_fall_dly_en==1'b0)&&(cnt_b==16'b0))begin
        out_r <= 1'b0;
    end else if((reg_fall_dly_en==1'b1)&&(cnt_b=={reg_dly,18'b0}))begin
        out_r <= 1'b0;
    end else;
end

assign out = out_r;
//    SRLC32E #(
//       .INIT(32'h00000000) // Initial Value of Shift Register
//    ) SRLC32E_inst (
//       .Q(Q),     // SRL data output
//       .Q31(Q31), // SRL cascade output pin
//       .A(A),     // 5-bit shift depth select input
//       .CE(CE),   // Clock enable input
//       .CLK(CLK), // Clock input
//       .D(D)      // SRL data input
//    );
endmodule
