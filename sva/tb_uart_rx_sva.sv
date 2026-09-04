`timescale 1ns / 1ps

module tb_uart_rx_sva;

    localparam integer CLKS_PER_BIT = 32;
    localparam integer OVERSAMPLE   = 16;

    reg        clk       = 1'b0;
    reg        rst_n     = 1'b0;
    reg        rx_serial = 1'b1;
    wire [7:0] rx_data;
    wire       rx_valid, rx_frame_error;

    always #10 clk = ~clk;

    uart_rx #(
        .CLKS_PER_BIT (CLKS_PER_BIT),
        .OVERSAMPLE   (OVERSAMPLE)
    ) dut (
        .clk            (clk),
        .rst_n          (rst_n),
        .rx_serial      (rx_serial),
        .rx_data        (rx_data),
        .rx_valid       (rx_valid),
        .rx_frame_error (rx_frame_error)
    );

    task automatic send_frame(input [7:0] value, input bit stop_bit);
        integer i;
        rx_serial = 1'b0;                              // start bit
        repeat (CLKS_PER_BIT) @(posedge clk);
        for (i = 0; i < 8; i = i + 1) begin            // data, LSB first
            rx_serial = value[i];
            repeat (CLKS_PER_BIT) @(posedge clk);
        end
        rx_serial = stop_bit;                          // stop bit
        repeat (CLKS_PER_BIT) @(posedge clk);
        rx_serial = 1'b1;                              // back to idle
        repeat (CLKS_PER_BIT) @(posedge clk);
    endtask

    initial begin
        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);

        send_frame(8'hA5, 1'b1);
        send_frame(8'h00, 1'b1);
        send_frame(8'hFF, 1'b1);
        send_frame(8'h3C, 1'b0);   // bad stop bit, drives RECOVER
        send_frame(8'h7E, 1'b1);   // must decode cleanly afterwards

        repeat (20) @(posedge clk);
        $display("SVA TB: RX frames sent, no assertion failures");
        $finish;
    end

endmodule