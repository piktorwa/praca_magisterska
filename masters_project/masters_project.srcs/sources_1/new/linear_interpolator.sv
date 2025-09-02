module linear_interpolator (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Assuming 12-bit ADC data
    input  logic pulse_detected,
    input  logic interp_en,
    output logic [15:0] interpolated_data,
    output logic valid_interpolated_data
);

    // Internal registers for interpolation
    logic [11:0] prev_adc_sample;
    logic [11:0] current_adc_sample;
    logic interpolating_active;

    // Output registers
    logic [11:0] interpolated_data_reg;
    logic valid_interpolated_data_reg;
    
    
    integer delta_val_signed;
    // Declare intermediate variables within the always_ff block or as local variables
    // to avoid 'undeclared variable' errors and ensure correct scope.
    // Using `integer` for loop variables and intermediate calculations is common in synthesisable code.
    // For signed arithmetic, explicitly cast to signed where needed.

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev_adc_sample <= 12'b0;
            current_adc_sample <= 12'b0;
            interpolating_active <= 1'b0;
            interpolated_data_reg <= 12'b0;
            valid_interpolated_data_reg <= 1'b0;
        end else begin
            valid_interpolated_data_reg <= 1'b0; // Default to not valid
            if (pulse_detected) begin
                if (interp_en) begin
                    prev_adc_sample <= current_adc_sample;
                    current_adc_sample <= adc_data;
                    interpolating_active <= 1'b1;
                    // Generate 3 new samples
                    // Perform linear interpolation
                    // interpolated_value = prev_adc_sample * 4 + (current_adc_sample - prev_adc_sample) * 6
                    // To avoid floating point, use fixed-point arithmetic or shift operations

                    delta_val_signed = ($signed(current_adc_sample) - $signed(prev_adc_sample)) / 4;
                    // Scale delta_val by interpolation_counter and then divide by 4
                    // For 12-bit ADC, max value is 4095. Delta can be up to 4095. 
                    // (4095 * 6) = 24570. This fits in 16 bits. 
                    // For intermediate calculations, using `integer` is safer as it's typically 32-bit.

                    interpolated_data <= $signed(prev_adc_sample) * 4 + delta_val_signed * 6;
                    valid_interpolated_data <= 1'b1;
                    interpolating_active <= 1'b0;
                    end else begin
                        // If not interpolating, just pass through the ADC data (or hold last value)
                        interpolated_data_reg <= adc_data;
                        valid_interpolated_data_reg <= 1'b1; // Always valid when not interpolating (or based on pulse_detected)
                end      
            end 
        end
    end

    //assign interpolated_data = interpolated_data_reg;
    //assign valid_interpolated_data = valid_interpolated_data_reg;

endmodule


