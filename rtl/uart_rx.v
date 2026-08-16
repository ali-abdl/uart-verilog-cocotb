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



always @(posedge clk) begin
        if (!rst_n) begin
            state          <= S_IDLE;
            rx_data        <= 8'd0;
            rx_valid       <= 1'b0;
            rx_frame_error <= 1'b0;
            shift_reg      <= 8'd0;
            bit_idx        <= 3'd0;
            os_count       <= 5'd0;
        end else begin
            rx_valid       <= 1'b0;       // defaults: one cycle pulses
            rx_frame_error <= 1'b0;

            case (state)

                S_IDLE: begin
                    os_count <= 5'd0;
                    bit_idx  <= 3'd0;
                    if (rx_sync == 1'b0) begin       // line went low: possible start
                        state <= S_START;
                    end
                end

                S_START: begin
                    if (tick) begin
                        if (os_count == (OVERSAMPLE/2) - 1) begin
                            if (rx_sync == 1'b0) begin
                                os_count <= 5'd0;    // now aligned to bit centres
                                state    <= S_DATA;
                            end else begin
                                state <= S_IDLE;     // glitch, not a real start bit
                            end
                        end else begin
                            os_count <= os_count + 1'b1;
                        end
                    end
                end

                S_DATA: begin
                    if (tick) begin
                        if (os_count == OVERSAMPLE - 1) begin
                            os_count  <= 5'd0;
                            shift_reg <= {rx_sync, shift_reg[7:1]};
                            if (bit_idx == 3'd7) begin
                                state <= S_STOP;
                            end else begin
                                bit_idx <= bit_idx + 1'b1;
                            end
                        end else begin
                            os_count <= os_count + 1'b1;
                        end
                    end
                end

                S_STOP: begin
                    if (tick) begin
                        if (os_count == OVERSAMPLE - 1) begin
                            os_count <= 5'd0;
                            rx_data  <= shift_reg;
                            rx_valid <= 1'b1;
                            if (rx_sync == 1'b1) begin
                                state <= S_IDLE;             // clean stop bit
                            end else begin
                                rx_frame_error <= 1'b1;
                                state          <= S_RECOVER;
                            end
                        end else begin
                            os_count <= os_count + 1'b1;
                        end
                    end
                end

                S_RECOVER: begin
                    if (rx_sync == 1'b1) begin   // wait for the line to return to idle
                        state <= S_IDLE;
                    end
                end

                default: state <= S_IDLE;

            endcase
        end
    end
endmodule