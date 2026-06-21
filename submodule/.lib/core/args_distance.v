/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_distance.v
// @author        3book
// @description   
// @created       2020-02-26T15:19:51.629Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:19:04.458Z+08:00
*******************************************************************************/

`timescale 1ns/100ps
module args_distance #(
parameter XW = 11   ,//X Data width 
parameter YW = 11   ,//Y Data width 
parameter DW = 2*XW+2*YW,//input Data width
parameter CW = 4    //input custom Data width
// parameter RW = XW>YW? XW+1 :YW+1 ,//result Data width
)(
input               clk,
input               rst,
input               rstn,
//slave AXI
input [DW-1:0]  s_axis_tdata    ,//point XY Data    
input [CW-1:0]  s_axis_tuser    ,//type
output          s_axis_tready   ,//ready
input           s_axis_tvalid   ,//valid
input           s_axis_tlast    ,//end of frame
//master AXI
output[15:0]    m_axis_tdata    ,//distance Data    
output          m_axis_tvalid   ,//valid
input           m_axis_tready   ,//ready
output[CW-1:0]  m_axis_tuser    ,//{sof,eof,sol,eol}
output          m_axis_tlast     //end of line
);

wire [XW-1:0]   x1;
wire [YW-1:0]   y1;
wire [XW-1:0]   x2;
wire [YW-1:0]   y2;
wire signed [XW:0]  xd;
wire signed [YW:0]  yd;
reg  signed [YW:0]  yd_1d = 'b0;

reg     s_tready = 'b0;
reg     s_tready_1d = 'b0;
reg     s_tready_2d = 'b0;
reg     s_axis_tvalid_1d = 'b0;
reg  signed [17:0]  mult_in = 'b0;
wire signed [35:0]  mult_out;

wire            s_tvalid;
reg             s_tvalid_1d = 'b0;
reg             s_tvalid_2d = 'b0;

reg  [2*XW-1:0]   square_xd = 'b0;
reg  [2*YW-1:0]   square_yd = 'b0;
localparam SW = XW > YW ? 2*XW : 2*YW ;
reg           square_sum_tvalid = 'b0;
reg  [SW:0]   square_sum_tdata = 'b0;
wire          square_sum_tlast;
wire [CW-1:0] square_sum_tuser;

wire [CW-1:0]   s_tuser;
wire            s_tlast;

wire [31:0]   s_axis_sr_tdata   ;
wire          s_axis_sr_tvalid  ;
wire          s_axis_sr_tready  ;
wire [CW-1:0] s_axis_sr_tuser   ;
wire          s_axis_sr_tlast   ;

//square_root((x1-x2)**2+(y1-y2)**2)
//get XY info
assign x1=s_axis_tdata[YW+:XW];
assign y1=s_axis_tdata[ 0+:YW];
assign x2=s_axis_tdata[XW+YW+YW+:XW];
assign y2=s_axis_tdata[XW+YW+:YW];
assign xd = $signed({1'b0,x1})-$signed({1'b0,x2})+$signed(1'b1);
assign yd = $signed({1'b0,y1})-$signed({1'b0,y2})+$signed(1'b1);

assign s_axis_tready=s_tready;
//slave axis ready
always @(posedge clk ) begin
    if (rst==1'b1) begin
        s_tready<= 1'b0;
    end else if (s_tready==1'b1 && s_axis_tvalid==1'b1) begin
        s_tready<= 1'b0;
    end else if (s_axis_sr_tready==1'b1) begin
        s_tready<= 1'b1;
    end else;
end
//square control
always @(posedge clk ) begin
    if (rst==1'b1) begin
        s_axis_tvalid_1d <= 1'b0;
    end else begin
        s_axis_tvalid_1d <= s_axis_tvalid;
    end
end
always @(posedge clk ) begin
    if (rst==1'b1) begin
        yd_1d <= 'b0;
    end else begin
        yd_1d <= yd;
    end
end
//square input
always @(posedge clk ) begin
    if(s_axis_tvalid==1'b1 && s_tready==1'b1)begin
        mult_in <= xd;
    end else begin
        mult_in <= yd_1d;
    end
    // end else if(s_axis_tvalid_1d==1'b1 && s_axis_sr_tready==1'b1)begin
        // mult_in <= yd;
    // end else;
end
//calculate square(latency=3)
MULT_MACRO #(
    .DEVICE("7SERIES"), // Target Device: "7SERIES" 
    .LATENCY(3  ), // Desired clock cycle latency, 0-4
    .WIDTH_A(18 ), // Multiplier A-input bus width, 1-25
    .WIDTH_B(18 )  // Multiplier B-input bus width, 1-18
) square (
    .P(mult_out ), // Multiplier output bus, width determined by WIDTH_P parameter
    .A(mult_in  ), // Multiplier input A bus, width determined by WIDTH_A parameter
    .B(mult_in  ), // Multiplier input B bus, width determined by WIDTH_B parameter
    .CE(1'b1    ), // 1-bit active high input clock enable
    .CLK(clk    ), // 1-bit positive edge clock input
    .RST(rst    )  // 1-bit input active high reset
);
// dsp_18x18_signed_mult square(
//     .CLK(clk),  // input wire CLK
//     .A  (mult_in), // input wire [17 : 0] A
//     .B  (mult_in), // input wire [17 : 0] B
//     .CE (1'b1   ), // input wire CE
//     .P  (mult_out) // output wire [35 : 0] P
//     );
//delay valid
args_delay #(
    .WIDTH  (1       ),//user data + tvalid
    .DELAY  (4)
    )valid_delay_u0(
    .clk    (clk        ),//clock
    .in     (s_axis_tvalid & s_tready),
    .out    (s_tvalid)
    );
//delay tvalid
always @(posedge clk ) begin
    if (rst==1'b1) begin
        s_tready_1d <= 1'b0;
        s_tready_2d <= 1'b0;
        s_tvalid_1d <= 1'b0;
        s_tvalid_2d <= 1'b0;
    end else begin
        s_tready_1d <= s_tready;
        s_tready_2d <= s_tready_1d;
        s_tvalid_1d <= s_tvalid;
        s_tvalid_2d <= s_tvalid_1d;
    end
end
//get square xd data
always @(posedge clk ) begin
    if(s_tvalid==1'b1)begin
        square_xd <= mult_out[0+:2*XW];
    end else ;
end
//get square sum data
always @(posedge clk ) begin
    if(s_tvalid_1d==1'b1)begin
        square_yd <= mult_out[0+:2*YW];
    end else ;
end
//get square sum data
always @(posedge clk ) begin
    if(s_tvalid_2d==1'b1)begin
        square_sum_tdata<= square_xd + square_yd;
    end else ;
end
//generate square sum valid
always @(posedge clk ) begin
    if(rst==1'b1)begin
        square_sum_tvalid <= 1'b0;
    end else if(s_tvalid_2d==1'b1)begin
        square_sum_tvalid <= 1'b1;
    end else begin
        square_sum_tvalid <= 1'b0;
    end
end
//delay user & last
args_delay #(
    .WIDTH  (CW+1       ),//user + last
    .DELAY  (7)
    )user_delay_u0(
    .clk    (clk        ),//clock
    .in     ({s_axis_tuser,s_axis_tlast}),
    .out    ({s_tuser,s_tlast})
    );
//assign square_sum user & last
assign square_sum_tuser=s_tuser;
assign square_sum_tlast=s_tlast;
//write square_sum into fifo 
axis_fifo_32w16d distance_fifo_u0(
    .s_axis_aresetn (rstn),  // input wire s_axis_aresetn
    .s_axis_aclk    (clk),        // input wire s_axis_aclk
    .s_axis_tvalid  (square_sum_tvalid),    // input wire s_axis_tvalid
    .s_axis_tready  (),    // output wire s_axis_tready
    .s_axis_tdata   ({{(32-SW-1){1'b0}},square_sum_tdata}),      // input wire [255 : 0] s_axis_tdata
    .s_axis_tlast   (square_sum_tlast),      // input wire s_axis_tlast
    .s_axis_tuser   (square_sum_tuser),      // input wire [3 : 0] s_axis_tuser
    .m_axis_tvalid  (s_axis_sr_tvalid),    // output wire m_axis_tvalid
    .m_axis_tready  (s_axis_sr_tready),    // input wire m_axis_tready
    .m_axis_tdata   (s_axis_sr_tdata),      // output wire [255 : 0] m_axis_tdata
    .m_axis_tlast   (s_axis_sr_tlast),      // output wire m_axis_tlast
    .m_axis_tuser   (s_axis_sr_tuser)      // output wire [3 : 0] m_axis_tuser
    );
//calculate square root
cordic_16_unsigned_square_root square_root_u0(
    .aclk                       (clk                ),  // input wire aclk
    .s_axis_cartesian_tvalid    (s_axis_sr_tvalid   ),  // input wire s_axis_cartesian_tvalid
    .s_axis_cartesian_tready    (s_axis_sr_tready   ),  // output wire s_axis_cartesian_tready
    .s_axis_cartesian_tuser     (s_axis_sr_tuser    ),  // input wire [3 : 0] s_axis_cartesian_tuser
    .s_axis_cartesian_tlast     (s_axis_sr_tlast    ),  // input wire s_axis_cartesian_tlast
    .s_axis_cartesian_tdata     (s_axis_sr_tdata[0+:24] ),// input wire [23 : 0] s_axis_cartesian_tdata

    .m_axis_dout_tvalid         (m_axis_tvalid      ),  // output wire m_axis_dout_tvalid
    .m_axis_dout_tready         (m_axis_tready      ),  // input wire m_axis_dout_tready
    .m_axis_dout_tuser          (m_axis_tuser       ),  // output wire [3 : 0] m_axis_dout_tuser
    .m_axis_dout_tlast          (m_axis_tlast       ),  // output wire m_axis_dout_tlast
    .m_axis_dout_tdata          (m_axis_tdata       )   // output wire [15 : 0] m_axis_dout_tdata
    );

endmodule