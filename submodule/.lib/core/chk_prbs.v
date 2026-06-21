/********************************************************************************
// @project       Object Detection & Tracking Uint(ODTU)
// @filename      chk_prbs.v
// @author        3book
// @description   
// @created       2020-01-26T10:32:50.187Z+08:00
// @copyright     Copyright (c) 2019 
// @last-modified 2020-03-31T22:19:53.652Z+08:00
*******************************************************************************/

`timescale 1ns/10ps
module chk_prbs #(
parameter POLY_LENGTH   = 31,
parameter POLY_TAP      = 28,
parameter INV_PATTERN   = 1,
// parameter NBITS         = 32,
parameter DW        = 10    ,//Data width 
parameter CW        = 4     ,//Control width {sof,eof,sol,eol}
parameter REG_DW    = 32     //register data width

)(
input               clk,
input               rst,
 
//Insert PRBS AXI-Stream 
input [DW-1:0]  s_axis_gen_tdata  ,//Data    
input           s_axis_gen_tvalid ,//valid
output          s_axis_gen_tready ,//ready
input [CW-1:0]  s_axis_gen_tuser  ,//{sof,eof,sol,eol}
input           s_axis_gen_tlast  ,//end of line
output[DW-1:0]  m_axis_gen_tdata  ,//Video Data    
output          m_axis_gen_tvalid ,//valid
input           m_axis_gen_tready ,//ready
output[CW-1:0]  m_axis_gen_tuser  ,//{sof,eof,sol,eol}
output          m_axis_gen_tlast  ,//end of line
//Check PRBS AXI-Stream 
input [DW-1:0]  s_axis_chk_tdata  ,//Data    
input           s_axis_chk_tvalid ,//valid
output          s_axis_chk_tready ,//ready
input [CW-1:0]  s_axis_chk_tuser  ,//{sof,eof,sol,eol}
input           s_axis_chk_tlast  ,//end of line
output[DW-1:0]  m_axis_chk_tdata  ,//Data    
output          m_axis_chk_tvalid ,//valid
input           m_axis_chk_tready ,//ready
output[CW-1:0]  m_axis_chk_tuser  ,//{sof,eof,sol,eol}
output          m_axis_chk_tlast  ,//end of line
//register
input  [REG_DW-1:0]   reg_cfg,//
// output [REG_DW*CW-1:0] reg_cnt,//
// output [REG_DW-1:0]   reg_sta,//
output [REG_DW-1:0]   reg_err //
);
localparam NBITS   = DW;
wire [NBITS-1:0]   gen_in  ;//generator Data input
wire [NBITS-1:0]   gen_out ;//generator Data output   
wire               gen_en  ;//generator Data enable
wire [NBITS-1:0]   chk_in  ;//generator Data input
wire [NBITS-1:0]   chk_out ;//generator Data output   
wire               chk_en  ;//generator Data enable
wire               reg_cfg_gen_en  ;
wire               reg_cfg_gen_err  ;
wire               reg_cfg_chk_en  ;
assign {reg_cfg_gen_err,reg_cfg_chk_en,reg_cfg_gen_en}=reg_cfg[2:0];
assign gen_in=(reg_cfg_gen_err==1'b1)? s_axis_gen_tdata :{NBITS{1'b0}};
assign gen_en=(reg_cfg_gen_en==1'b1)? (s_axis_gen_tvalid & s_axis_gen_tready) : 1'b0;

assign m_axis_gen_tdata =(reg_cfg_gen_en==1'b1)? gen_out : s_axis_gen_tdata ;
assign m_axis_gen_tvalid=s_axis_gen_tvalid;
assign m_axis_gen_tuser =s_axis_gen_tuser ;
assign m_axis_gen_tlast =s_axis_gen_tlast ;
assign s_axis_gen_tready=m_axis_gen_tready;
// Instantiate the PRBS generator
PRBS_ANY #(
    .CHK_MODE   (0          ),
    .INV_PATTERN(INV_PATTERN),
    .POLY_LENGTH(POLY_LENGTH),
    .POLY_TAP   (POLY_TAP),
    .NBITS      (NBITS))
    gen_prbs(
    .RST        (rst        ),
    .CLK        (clk        ),
    .DATA_IN    (gen_in     ),
    .EN         (gen_en     ),
    .DATA_OUT   (gen_out    )
    ); 

assign chk_in=s_axis_chk_tdata;
assign chk_en=(reg_cfg_chk_en==1'b1)? (s_axis_chk_tvalid & s_axis_chk_tready) : 1'b0;

assign m_axis_chk_tdata =s_axis_chk_tdata ;
assign m_axis_chk_tvalid=s_axis_chk_tvalid;
assign m_axis_chk_tuser =s_axis_chk_tuser ;
assign m_axis_chk_tlast =s_axis_chk_tlast ;
assign s_axis_chk_tready=m_axis_chk_tready;

// Instantiate the PRBS checker
PRBS_ANY #(
    .CHK_MODE   (1          ),
    .INV_PATTERN(INV_PATTERN),
    .POLY_LENGTH(POLY_LENGTH),
    .POLY_TAP   (POLY_TAP   ),
    .NBITS      (NBITS      ))
    chk_prbs(
    .RST        (rst        ),
    .CLK        (clk        ),
    .DATA_IN    (chk_in     ),
    .EN         (chk_en     ),
    .DATA_OUT   (chk_out    )
    ); 
assign reg_err=|chk_out;
endmodule