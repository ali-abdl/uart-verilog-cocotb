`timescale 1ns / 1ps

module uart #(
    parameter integer CLKS_PER_BIT = 32,
    parameter integer OVERSAMPLE   = 16
)(
    input  wire       clk,
    input  wire       rst_n,

    // ---- Transmit ----
    input  wire       tx_start,
    input  wire [7:0] tx_data,
    output wire       tx_busy,
    output wire       tx_done,
    output wire       tx_serial,

    // ---- Receive ----
    input  wire       rx_serial,
    output wire [7:0] rx_data,
    output wire       rx_valid,
    output wire       rx_frame_error
);

    uart_tx #(
        .CLKS_PER_BIT (CLKS_PER_BIT)
    ) u_tx (
        .clk       (clk),
        .rst_n     (rst_n),
        .tx_start  (tx_start),
        .tx_data   (tx_data),
        .tx_serial (tx_serial),
        .tx_busy   (tx_busy),
        .tx_done   (tx_done)
    );

    uart_rx #(
        .CLKS_PER_BIT (CLKS_PER_BIT),
        .OVERSAMPLE   (OVERSAMPLE)
    ) u_rx (
        .clk            (clk),
        .rst_n          (rst_n),
        .rx_serial      (rx_serial),
        .rx_data        (rx_data),
        .rx_valid       (rx_valid),
        .rx_frame_error (rx_frame_error)
    );

endmodule