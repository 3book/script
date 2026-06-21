/********************************************************************************
// @project       
// @filename      args_shift.v
// @author        3book
// @description   
// @copyright     Copyright (c)  
// @created       2022-08-15T14:04:58.109Z+08:00
// @last-modified 2022-08-16T10:27:30.945Z+08:00
*******************************************************************************/
module args_pipe #(
parameter W = 10   ,//Width
parameter N = 10    //Number
)(
input   c,//clock
input   [W-1:0]  i,//input data
output  [W-1:0]  o //output data
);
localparam NW = W * N;
reg   [NW-1:0] sft={NW{1'b0}}  ;
generate
if(N==1)begin
    always@(posedge c)begin
        sft <= i;
    end
end else begin
    always@(posedge c)begin
        sft <= {sft[NW-W-1:0],i};
    end
end
endgenerate
assign o = sft[NW-1 -:W];
endmodule