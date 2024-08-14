`timescale 1ns / 1ps

module ADC_clock_gen(
    input wire clk,  // 输入时钟信号
    input wire reset,   // 重置信号
    output reg clk_out  // 输出分频后的时钟信号
);

reg [13:0] counter; // 14位计数器

always @(posedge clk or posedge reset) begin
    if (reset) begin
        counter <= 14'b0;
        clk_out <= 0;
    end else begin
        if (counter == 14'd16383) begin
            counter <= 14'b0;
            clk_out <= ~clk_out; // 反转输出时钟信号
        end else begin
            counter <= counter + 1;
        end
    end
end

endmodule
