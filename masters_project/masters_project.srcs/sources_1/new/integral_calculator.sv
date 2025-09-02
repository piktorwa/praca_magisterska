module integral_calculator (
    input  logic clk,
    input  logic rst_n,
    input  logic [15:0] data_in, // Input data (e.g., processed_data from interpolator)
    input  logic integrate_en, // Enable integration
    input  logic [2:0] pulse_state,
    output logic [31:0] integral_out, // Accumulated integral value
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic [31:0] integral_sum;
    logic [1:0] perv_pulse_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integral_sum <= 32'b0;
            integral_ready <= 1'b0;
        end else begin            
            // Detect rising edge of integrate_en to start integration
            if (integrate_en) begin
                // Ensure data_in is properly extended to 32 bits before addition to prevent overflow
                integral_sum <= integral_sum + {16'b0, data_in}; // Zero-extend 12-bit data to 32 bits
                if (pulse_state == 0 && perv_pulse_state == 3) begin
                    integral_ready <= 1'b1;
                end
                perv_pulse_state <= pulse_state;
            end else if (integral_ready) begin
                integral_ready <= 1'b0;
            end
        end
    end

    assign integral_out = integral_sum;

endmodule

