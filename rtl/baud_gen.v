`timescale 1ns / 1ps

module baud_gen #(

    parameter integer DIVISOR = 27
)(

    input wire clk,
    input wire rst_n,
    output reg tick
);
reg [15:0] count;

always @(posedge clk) begin
    if (!rst_n) begin
        count <= 16'd0;
        tick <= 1'b0;
    end else if (count == DIVISOR -1) begin
        count <= 16'd0 ;
        tick <= 1'b1;
    end else begin
        count <= count + 1'b1;
        tick <= 1'b0;
    end
end

endmodule 