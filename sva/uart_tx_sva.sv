`timescale 1ns / 1ps

module uart_tx_sva (
    input wire clk,
    input wire rst_n,
    input wire tx_start,
    input wire tx_serial,
    input wire tx_busy,
    input wire tx_done
);

    // 1. The line idles high whenever no frame is in flight.
    property p_idle_high;
        @(posedge clk) disable iff (!rst_n)
            !tx_busy |-> tx_serial;
    endproperty
    a_idle_high: assert property (p_idle_high)
        else $error("tx_serial was not high while idle");

    // 2. A start pulse while idle must raise tx_busy on the next cycle.
    property p_start_raises_busy;
        @(posedge clk) disable iff (!rst_n)
            (tx_start && !tx_busy) |=> tx_busy;
    endproperty
    a_start_raises_busy: assert property (p_start_raises_busy)
        else $error("tx_busy did not assert after tx_start");

    // 3. tx_done is exactly one cycle wide.
    property p_done_one_cycle;
        @(posedge clk) disable iff (!rst_n)
            tx_done |=> !tx_done;
    endproperty
    a_done_one_cycle: assert property (p_done_one_cycle)
        else $error("tx_done was wider than one cycle");

    // 4. tx_done can only occur at the end of a frame.
    property p_done_ends_frame;
        @(posedge clk) disable iff (!rst_n)
            tx_done |-> $past(tx_busy);
    endproperty
    a_done_ends_frame: assert property (p_done_ends_frame)
        else $error("tx_done asserted with no frame in flight");

endmodule


bind uart_tx uart_tx_sva u_tx_sva (
    .clk       (clk),
    .rst_n     (rst_n),
    .tx_start  (tx_start),
    .tx_serial (tx_serial),
    .tx_busy   (tx_busy),
    .tx_done   (tx_done)
);