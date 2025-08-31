module integral_calculator (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] data_in, // Input data (e.g., processed_data from interpolator)
    input  logic integrate_en, // Enable integration
    output logic [31:0] integral_out, // Accumulated integral value
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic [31:0] integral_sum;
    logic prev_integrate_en;
    logic integration_active;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integral_sum <= 32'b0;
            prev_integrate_en <= 1'b0;
            integration_active <= 1'b0;
            integral_ready <= 1'b0;
        end else begin
            prev_integrate_en <= integrate_en;
            
            // Detect rising edge of integrate_en to start integration
            if (integrate_en && !prev_integrate_en) begin
                integration_active <= 1'b1;
                 integral_ready <= 1'b0;
                integral_sum <= 32'b0; // Initialize to 0 at the start of integration
            end 
            // Continue integration while enabled
            else if (integrate_en && integration_active) begin
                // Ensure data_in is properly extended to 32 bits before addition to prevent overflow
                integral_sum <= integral_sum + {20'b0, data_in}; // Zero-extend 12-bit data to 32 bits
                integral_ready <= 1'b0;
            end 
            // Detect falling edge of integrate_en to complete integration
            else if (!integrate_en && prev_integrate_en && integration_active) begin
                integration_active <= 1'b0;
                integral_ready <= 1'b1; // Signal that integral calculation is complete
            end
            // Reset integral when not enabled and not in active integration
            // Do not reset integral_sum here. It should hold its value until a new integration starts or rst_n is asserted.
            // integral_ready <= 1'b0; // This line is already handled by other conditions or will be set to 0 after one cycle.
            // Hold integral_ready for one clock cycle after completion
            else if (integral_ready) begin
                integral_ready <= 1'b0;
            end
        end
    end

    assign integral_out = integral_sum;

endmodule

