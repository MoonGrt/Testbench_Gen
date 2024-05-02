`timescale 1ns / 1ps

module blood_oxygen #(
    parameter CONVERT_PARAM = 1,
    parameter THRESHOLD = 95,
    parameter SATURATION = 100,
    parameter CLK_FREQ = 50_000_000,
    parameter LASER_ON_PARAM  = 400, // laser on time
    parameter LASER_OFF_PARAM = 100, // laser on time
    parameter ADC_WIDTH = 8
)(
    input wire [(ADC_WIDTH-1):0] adc_data,
    input wire en, clk,
    output reg red_laser = 0, IR_laser = 0,
    output wire red_led,
    output wire [15:0] ox_data
);

localparam LASER_ON_TIME  = CLK_FREQ / 1000 * LASER_ON_PARAM;
localparam LASER_OFF_TIME = CLK_FREQ / 1000 * LASER_OFF_PARAM;

reg [$clog2(CLK_FREQ)+1:0] laser_cnt;
reg laser_state;
assign ox_data = adc_data * CONVERT_PARAM;
assign red_led = ox_data > THRESHOLD * SATURATION / 100;

always @(posedge clk or negedge en) begin
    if (~en)
        laser_cnt <= 0;
    else if (laser_cnt == LASER_ON_TIME+LASER_OFF_TIME - 1) // 500ms
        laser_cnt <= 0;
    else
        laser_cnt <= laser_cnt + 1;
end

always @(posedge clk or negedge en) begin
    if (~en) begin
        red_laser <= 1'b0; // positive logic
        IR_laser <= 1'b0;
        laser_state <= 1'b0;
    end
    else begin
        if (laser_cnt == LASER_ON_TIME+LASER_OFF_TIME - 1)
            laser_state <= ~laser_state; // laser_state change
        if (laser_cnt < LASER_ON_TIME)
            if (laser_state)
                red_laser <= 1'b1;
            else
                IR_laser <= 1'b1;
        else begin
            red_laser <= 1'b0;
            IR_laser <= 1'b0;
        end
    end
end

endmodule
