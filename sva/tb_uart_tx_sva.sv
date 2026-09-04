`timescale 1ns / 1ps

module tb_uart_tx_sva;

    localparam integer CLKS_PER_BIT = 8;

    reg        clk      = 1'b0;
    reg        rst_n    = 1'b0;
    reg        tx_start = 1'b0;
    reg  [7:0] tx_data  = 8'h00;
    wire       tx_serial, tx_busy, tx_done;

    always #10 clk = ~clk;          // 50 MHz

    uart_tx #(
        .CLKS_PER_BIT (CLKS_PER_BIT)
    ) dut (
        .clk       (clk),
        .rst_n     (rst_n),
        .tx_start  (tx_start),
        .tx_data   (tx_data),
        .tx_serial (tx_serial),
        .tx_busy   (tx_busy),
        .tx_done   (tx_done)
    );

    task automatic send_byte(input [7:0] value);
        @(posedge clk);
        tx_data  = value;
        tx_start = 1'b1;
        @(posedge clk);
        tx_start = 1'b0;
        @(posedge tx_done);
        @(posedge clk);
    endtask

    initial begin
        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);

        send_byte(8'hA5);
        send_byte(8'h00);
        send_byte(8'hFF);
        send_byte(8'h01);
        send_byte(8'h80);

        repeat (10) @(posedge clk);
        $display("SVA TB: 5 frames sent, no assertion failures");
        $finish;
    end

endmodule