/********************************************************************************
// @project       
// @filename      beat_chk.v
// @author        3book
// @description   
// @copyright     Copyright (c)  
// @created       2024-12-23T23:15:23.300Z+08:00
// @last-modified 2025-05-19T00:11:22.459Z+08:00
*******************************************************************************/
`timescale 1ns/10ps
module beat_chk #(
    parameter CLK_FREQ = 1000000,//clock frequence Hz
    parameter CHK_FREQ = 1000   ,//check frequence Hz
    parameter CHK_TIME = 5      ,//check times
    parameter LED_FREQ = 1      ,//frequence Hz
    )(
    inout  clk,
    input  rst,
    input  in,
    output alive 
);
localparam MAX_A = CLK_FREQ/CHK_FREQ;
localparam AW = $clog2(MAX_A);
localparam MAX_B = CLK_FREQ/CHK_FREQ/2*CHK_TIME;
localparam BW = $clog2(MAX_B);
// wire edge_i;
// wire edge_rise;
// wire edge_fall;
// assign edge_i = in;
// args_edge #(
//     .EDGE   ("rise")
// )args_edge_rise(
//     .c  (clk),
//     .r  (1'b0),
//     .i  (edge_i),
//     .o  (edge_rise)
//     );
// args_edge #(
//     .EDGE   ("fall")
// )args_edge_fall(
//     .c  (clk),
//     .r  (1'b0),
//     .i  (edge_i),
//     .o  (edge_fall)
//     );
reg [AW-1:0] cnt_a;
wire timeout;
always @(posedge clk) begin
    if(in==1'b1)begin
        cnt_a <= 'b0;
    end else if(timeout==1'b0)begin
        cnt_a <= cnt_a + 1'b1;
    end else;
end
assign timeout=(cnt_a==MAX_A);

always @(posedge clk) begin
    if(timeout==1'b1)begin
        alive_p <= 1'b0;
    end else begin
        alive_p <= 1'b1;
    end
end
assign alive =alive_p;




// reg [BW-1:0] cnt_b;
// always @(posedge clk) begin
//     if(cnt_b!=MAX_B)begin

//     if(cnt_a==MAX_A)begin
//         cnt_b <= cnt_b + 1'b1;
//     end else begin
//         cnt_b <= 'b0;
//     end
// end

//generate 1Hz for LED
// localparam LED_LSB = $clog2(CLK_FREQ*1000000/LED_FREQ/2);
// reg [LED_LSB:0] led_cnt = 'h0 ;

// always @(posedge clkin) begin
//     led_cnt <= led_cnt + 1'b1;
// end
// assign led_1hz = led_cnt[LED_LSB];  //for hardware

// localparam DEAD = 4'b0001;
// localparam D2A  = 4'b0010;
// localparam ALIVE= 4'b0100;
// localparam A2D  = 4'b1000;

// reg [1:0] sta = DEAD;

// always @(posedge clk)begin
//     if (rst==1'b1) begin
//         sta <= DEAD;
//     end else
//     case (sta)
//     DEAD : begin
//         if (beat==1'b1)
//             sta <= D2A;
//         else;
//     end
//     D2A : begin
//         if (beat_cnt==2'b11)
//             sta <= ALIVE;
//         else if(timeout==1'b1)
//             sta <= DEAD;
//         else ;
//     end
//     ALIVE : begin
//         if (beat==1'b1)
//             sta <= ALIVE;
//         else if(timeout==1'b1)
//             sta <= DEAD;
//         else ;
//     end
//     A2D : begin
//         if (beat_cnt==2'b01)
//             sta <= ALIVE;
//         else if(timeout==1'b1)
//             sta <= DEAD;
//         else ;
//     end
//     endcase
// end
// always @(posedge clk) begin
//     if(sta==DEAD)begin
//         cnt <= 'b0;
//     end else if(sta==D2A) begin
//         if(cnt==MAX_A)begin
//             cnt <= 'b0;
//         end else begin
//             cnt <= cnt + 1'b1;
//         end
//     end else if(sta==D2A) begin
//         if(cnt==MAX_B)begin
//             cnt <= 'b0;
//         end else begin
//             cnt <= cnt + 1'b1;
//         end
//     end else if(sta==D2A) begin
//         if(cnt==MAX_C)begin
//             cnt <= 'b0;
//         end else begin
//             cnt <= cnt + 1'b1;
//         end
//     end
        
//     if(cnt==MAX_A)begin
//         cnt_b <= cnt_b + 1'b1;
//     end else begin
//         cnt_b <= 'b0;
//     end
// end
endmodule