`timescale 1ns / 1ps

module dump;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars;
    end
endmodule
