`timescale 1ns / 1ps

module uart_rx_sva #(
    parameter integer OVERSAMPLE = 16
)(
    input wire       clk,
    input wire       rst_n,
    input wire       rx_sync,
    input wire       rx_valid,
    input wire       rx_frame_error,
    input wire [2:0] state,
    input wire [4:0] os_count
);

    localparam [2:0] S_IDLE    = 3'd0,
                     S_START   = 3'd1,
                     S_DATA    = 3'd2,
                     S_STOP    = 3'd3,
                     S_RECOVER = 3'd4;

    // 1. rx_valid is exactly one cycle wide.
    a_valid_one_cycle: assert property (
        @(posedge clk) disable iff (!rst_n)
            rx_valid |=> !rx_valid
    ) else $error("rx_valid was wider than one cycle");

    // 2. A framing error is only ever reported alongside a valid byte.
    a_error_with_valid: assert property (
        @(posedge clk) disable iff (!rst_n)
            rx_frame_error |-> rx_valid
    ) else $error("rx_frame_error asserted without rx_valid");

    // 3. The oversample counter never runs past its range.
    a_oscount_in_range: assert property (
        @(posedge clk) disable iff (!rst_n)
            os_count < OVERSAMPLE
    ) else $error("os_count exceeded OVERSAMPLE-1");

    // 4. The FSM never lands on an undefined encoding.
    a_state_legal: assert property (
        @(posedge clk) disable iff (!rst_n)
            state <= S_RECOVER
    ) else $error("FSM entered an illegal state");

    // 5. A framing error must put the FSM into RECOVER.
    a_error_enters_recover: assert property (
        @(posedge clk) disable iff (!rst_n)
            rx_frame_error |-> (state == S_RECOVER)
    ) else $error("framing error did not enter RECOVER");

    // 6. While the line is still low, RECOVER must hold.
    a_recover_holds: assert property (
        @(posedge clk) disable iff (!rst_n)
            (state == S_RECOVER && !rx_sync) |=> (state == S_RECOVER)
    ) else $error("left RECOVER while the line was still low");

    // 7. Once the line returns high, RECOVER must release to IDLE.
    a_recover_exits: assert property (
        @(posedge clk) disable iff (!rst_n)
            (state == S_RECOVER && rx_sync) |=> (state == S_IDLE)
    ) else $error("stuck in RECOVER after the line returned high");

endmodule


bind uart_rx uart_rx_sva #(
    .OVERSAMPLE (OVERSAMPLE)
) u_rx_sva (
    .clk            (clk),
    .rst_n          (rst_n),
    .rx_sync        (rx_sync),
    .rx_valid       (rx_valid),
    .rx_frame_error (rx_frame_error),
    .state          (state),
    .os_count       (os_count)
);