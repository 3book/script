/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      args_conv.v
// @author        3book
// @description   Convolution algorithm
// @created       2019-07-16T14:47:54.337Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2019-10-11T14:47:42.201Z+08:00
*******************************************************************************/
// latency=DSP_LATENCY + $clog2(N)+1
`timescale 1ns/100ps
module args_conv #(
parameter DW = 10   ,//Data width 
parameter KDW= 10   ,//kernel data width
parameter NU = 9    ,//Data numbers
parameter SW = 0    ,//Data numbers
parameter RW = 10   ,//DW+KDW+$clog2(NU) //result Data width
parameter MULT = "DSP",//Multiply used DSP|BITAND
parameter DSP_LATENCY = 3,//// Desired clock cycle latency, 0-4
parameter ACCURACY = "HIGH"//Multiply used DSP
)(
input                   clk,
input                   rst,
input   [DW*NU-1:0]     in,//input data
input   [KDW*NU-1:0]    ke,//kernel data
input                   ce,//enable
output  [RW-1:0]        out//sum(k1+k2+k3+k4+k5+k6+k7+k8+k9)=1024
);

// localparam  KH   = ksize[7:4];
// localparam  KW   = ksize[3:0];
// localparam  TDW =   DW+KDW+$clog2(NU) //out data width
localparam MW = DW+KDW+2;
// localparam  cw  =   DW+KDW+clog2(KW);
localparam CRW = MW+$clog2(NU)    ;//result Data width

wire    [MW*NU-1:0] p;//data width without carry chain
wire    [DW*NU-1:0] q;//data width without carry chain
wire    [CRW-1:0]   o;
//1 4 7
//2 5 8
//3 6 9
//3*3卷积
//y=x0*k0+x1*k1+x2*k2+x3*k3+x4*k4+x5*k5+x6*k6+x7*k7+x8*k8+x9*k9
//除法转乘法和移位
//X=y/9=y*1024/9/1024=(y*113)>>10
genvar i;
generate
    if(MULT=="BITAND")begin
        assign q = in & ke;
        assign p = 'b0;
    end else begin
        for (i = 0; i<NU; i=i+1) begin
            if(MULT=="DSP")begin

            MULT_MACRO #(
                .DEVICE("7SERIES"   ), // Target Device: "7SERIES" 
                .LATENCY(DSP_LATENCY), // Desired clock cycle latency, 0-4
                .WIDTH_A(DW+1       ), // Multiplier A-input bus width, 1-25
                .WIDTH_B(KDW+1      )  // Multiplier B-input bus width, 1-18
            ) MULT_MACRO_inst (
                .P(p[i*MW+:MW]),     // Multiplier output bus, width determined by WIDTH_P parameter
                .A({1'b0,in[i*DW+:DW]}),     // Multiplier input A bus, width determined by WIDTH_A parameter
                .B({1'b0,ke[i*KDW+:KDW]}),     // Multiplier input B bus, width determined by WIDTH_B parameter
                .CE(ce),   // 1-bit active high input clock enable
                .CLK(clk), // 1-bit positive edge clock input
                .RST(rst)  // 1-bit input active high reset
            );
            end else begin
                assign p[i*MW+:MW] = in[i*DW+:DW] * ke[i*KDW+:KDW];
            end
            assign q[i*DW+:DW] = p[i*MW+KDW+:DW];
        end
    end
endgenerate
if(ACCURACY=="HIGH")begin
args_plus #(
.W  (MW ),  //argument Data Width
.N  (NU )   //argument Number
)args_plus_inst(
.clk(clk),
.rst(rst),
.in (p  ),
.out(o  )
);
// assign out=o[SW+:RW];
end
if(ACCURACY=="LOW")begin
args_plus #(
.W  (DW ),  //argument Data Width
.N  (NU )   //argument Number
)args_plus_inst(
.clk(clk),
.rst(rst),
.in (q  ),
.out(o[SW+:RW]  )
);
// assign out=o;
end
assign out=o[SW+:RW];
endmodule