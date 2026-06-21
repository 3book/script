`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    11:13:00 08/23/2022 
// Design Name: 
// Module Name:    lfsr_16bit 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: feedback taps: 16, 14, 13, 11
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Revision 0.02 - added async reset signal 'rst_n' and read buffer full
// beacon 'rd_buf_full', modified master read part of codes.
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module lfsr_16bit #(
	parameter         SEED = 16'hce  // seed
	(
	input wire        iReset,  // system reset
        input wire        iClk,    // system clock		
	input wire        iEn,     // enable
	output wire[15:0] oData    // data
    );
	
	// --------define internal register and buffer--------
	// counter
        //reg [15:0]       seed_reg;
	reg [15:0]        lfsr_reg;
	
	assign            oData     = lfsr_reg; 

	// polynomials
	always @(posedge iCLK)begin
          if(iReset == 'b1) begin
            lfsr_reg  <= SEED;
          end
	  else begin
	    if(iEn)
              lsfr_reg[15]  <= lsfr_reg[14] ^ 1'b0;
              lsfr_reg[14]  <= lsfr_reg[13] ^ lsfr_reg[15];
              lsfr_reg[13]  <= lsfr_reg[12] ^ lsfr_reg[15];
              lsfr_reg[12]  <= lsfr_reg[11] ^ 1'b0;
              lsfr_reg[11]  <= lsfr_reg[10] ^ lsfr_reg[15];
              lsfr_reg[10]  <= lsfr_reg[9]  ^ 1'b0;
	      lsfr_reg[9 ]  <= lsfr_reg[8]  ^ 1'b0;
              lsfr_reg[8 ]  <= lsfr_reg[7]  ^ 1'b0;
	      lsfr_reg[7 ]  <= lsfr_reg[6]  ^ 1'b0;
              lsfr_reg[6 ]  <= lsfr_reg[5]  ^ 1'b0;
	      lsfr_reg[5 ]  <= lsfr_reg[4]  ^ 1'b0;
              lsfr_reg[4 ]  <= lsfr_reg[3]  ^ 1'b0;
	      lsfr_reg[3 ]  <= lsfr_reg[2]  ^ 1'b0;
              lsfr_reg[2 ]  <= lsfr_reg[1]  ^ 1'b0;
	      lsfr_reg[1 ]  <= lsfr_reg[0]  ^ 1'b0;
              lsfr_reg[0 ]  <= lsfr_reg[15];
          end                
        end                  
	


endmodule
