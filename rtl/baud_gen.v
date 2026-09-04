`timescale 1ns / 1ps

module baud_gen #(

    parameter integer DIVISOR = 27
)(

    input wire clk,
    input wire rst_n,
    input  wire en,
    output reg tick
);
localparam [15:0] MAXCOUNT = 16'(DIVISOR - 1);

reg [15:0] count;

always @(posedge clk) begin
    if (!rst_n) begin
        count <= 16'd0;
        tick <= 1'b0;
    end else if (!en) begin
            count <= 16'd0;
            tick  <= 1'b0;
    end else if (count == MAXCOUNT) begin
        count <= 16'd0 ;
        tick <= 1'b1;
    end else begin
        count <= count + 1'b1;
        tick <= 1'b0;
    end
end

endmodule 