`timescale 1ns / 1ps

module uart_tx #(
    parameter integer CLKS_PER_BIT = 434
)(

    input wire clk,
    input wire rst_n,
    input wire tx_start,
    input wire [7:0] tx_data,
    output reg tx_serial,
    output reg tx_busy,
    output reg tx_done
);

    // state encoding
    
    localparam [1:0] S_IDLE = 2'd0,
                     S_START = 2'd1,
                     S_DATA = 2'd2,
                     S_STOP = 2'd3;

    // internal state 
    reg [1:0] state; // which state we're in
    reg [7:0] shift_reg; // the byte, shifted right as we send
    reg [2:0] bit_idx;  // which data bit we're on 0-7

    // bit time generator
    wire tick;
    wire baud_en;

    assign baud_en = tx_busy | tx_start;

    baud_gen #(
        .DIVISOR (CLKS_PER_BIT)
    ) u_baud (
        .clk (clk),
        .rst_n (rst_n),
        .en (baud_en),
        .tick (tick)
    );

always @(posedge clk) begin
    if (!rst_n) begin
        state <= S_IDLE;
        tx_serial <= 1'b1;
        tx_busy <= 1'b0;
        tx_done <= 1'b0;
        shift_reg <= 8'd0;
        bit_idx <= 3'd0;
    end else begin
        tx_done <= 1'b0;  // default, overriden below
        
        case (state)
            
            S_IDLE: begin
                tx_serial <= 1'b1; // line idles high
                if (tx_start) begin
                    shift_reg <= tx_data;
                    bit_idx <= 3'd0;
                    tx_busy <= 1'b1;
                    tx_serial <= 1'b0;
                    state <= S_START;
                end
            end

            S_START: begin
                if (tick) begin
                    tx_serial <= shift_reg[0]; // first data bit
                    state <= S_DATA;
                end
            end

            S_DATA: begin
                if (tick) begin
                    if (bit_idx == 3'd7) begin
                        tx_serial <= 1'b1;  // stop bit
                        state <= S_STOP;
                    end else begin
                        bit_idx <= bit_idx + 1'b1;
                        shift_reg <= {1'b0, shift_reg[7:1]};
                        tx_serial <= shift_reg[1];
                    end
                end
            end

            S_STOP: begin
                if (tick) begin
                    tx_busy <= 1'b0;
                    tx_done <= 1'b1;
                    state <= S_IDLE;
                end
            end

            default: state <= S_IDLE;

        endcase
    end

end
endmodule