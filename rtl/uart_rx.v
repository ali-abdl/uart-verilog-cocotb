`timescale 1ns / 1ps

module uart_rx #(
    parameter integer CLKS_PER_BIT = 32,
    parameter integer OVERSAMPLE   = 16
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rx_serial,
    output reg  [7:0] rx_data,
    output reg        rx_valid,
    output reg        rx_frame_error
);

    localparam integer DIVISOR = CLKS_PER_BIT / OVERSAMPLE;

    localparam [2:0] S_IDLE    = 3'd0,
                     S_START   = 3'd1,
                     S_DATA    = 3'd2,
                     S_STOP    = 3'd3,
                     S_RECOVER = 3'd4;

    //  Two flip flop synchronizer for the async input 
    reg rx_meta, rx_sync;

    always @(posedge clk) begin
        if (!rst_n) begin
            rx_meta <= 1'b1;
            rx_sync <= 1'b1;
        end else begin
            rx_meta <= rx_serial;
            rx_sync <= rx_meta;
        end
    end

    //  Internal state 
    reg [2:0] state;
    reg [7:0] shift_reg;
    reg [2:0] bit_idx;
    reg [4:0] os_count;    // counts 0..OVERSAMPLE-1

    //  Oversampling tick: free running at 16x the baud rate 
    wire tick;

    baud_gen #(
        .DIVISOR (DIVISOR)
    ) u_baud (
        .clk   (clk),
        .rst_n (rst_n),
        .en    (1'b1),
        .tick  (tick)
    );

endmodule