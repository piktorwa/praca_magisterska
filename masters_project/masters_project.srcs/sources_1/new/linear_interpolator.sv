module linear_interpolator (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Assuming 12-bit ADC data
    input  logic pulse_detected,
    input  logic [11:0] pulse_start_val,
    input  logic [11:0] pulse_peak_val,
    input  logic [31:0] pulse_duration_cycles,
    output logic [11:0] interpolated_data,
    output logic valid_interpolated_data
);

    // Internal registers for interpolation
    logic [11:0] prev_adc_sample;
    logic [11:0] current_adc_sample;
    logic [2:0] interpolation_counter; // 0 to 4 for 4 new samples + 1 original
    logic interpolating_active;

    // Output registers
    logic [11:0] interpolated_data_reg;
    logic valid_interpolated_data_reg;

    // Declare intermediate variables within the always_ff block or as local variables
    // to avoid 'undeclared variable' errors and ensure correct scope.
    // Using `integer` for loop variables and intermediate calculations is common in synthesisable code.
    // For signed arithmetic, explicitly cast to signed where needed.

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev_adc_sample <= 12'b0;
            current_adc_sample <= 12'b0;
            interpolation_counter <= 3'b0;
            interpolating_active <= 1'b0;
            interpolated_data_reg <= 12'b0;
            valid_interpolated_data_reg <= 1'b0;
        end else begin
            valid_interpolated_data_reg <= 1'b0; // Default to not valid

            if (pulse_detected) begin
                // When a new pulse is detected, reset interpolation and start with the first sample
                prev_adc_sample <= adc_data;
                current_adc_sample <= adc_data;
                interpolation_counter <= 3'b0;
                interpolating_active <= 1'b1;
                interpolated_data_reg <= adc_data; // Output the first sample immediately
                valid_interpolated_data_reg <= 1'b1;
            end else if (interpolating_active) begin
                if (interpolation_counter < 4) begin // Generate 4 new samples
                    // Perform linear interpolation
                    // interpolated_value = prev_adc_sample + (current_adc_sample - prev_adc_sample) * (interpolation_counter / 5)
                    // To avoid floating point, use fixed-point arithmetic or shift operations

                    // Declare variables locally within the block where they are used
                    integer delta_val_signed;
                    integer interpolated_offset_signed;

                    delta_val_signed = $signed(current_adc_sample) - $signed(prev_adc_sample);
                    // Scale delta_val by interpolation_counter and then divide by 5
                    // For 12-bit ADC, max value is 4095. Delta can be up to 4095. 
                    // (4095 * 4) = 16380. This fits in 16 bits. 
                    // For intermediate calculations, using `integer` is safer as it's typically 32-bit.
                    interpolated_offset_signed = (delta_val_signed * interpolation_counter) / 5;

                    interpolated_data_reg <= $signed(prev_adc_sample) + interpolated_offset_signed;
                    valid_interpolated_data_reg <= 1'b1;
                    interpolation_counter <= interpolation_counter + 1;
                end else begin // Output the next original sample
                    prev_adc_sample <= adc_data; // Current ADC data becomes previous for next interpolation
                    current_adc_sample <= adc_data; // Current ADC data is the new current
                    interpolation_counter <= 3'b0;
                    interpolated_data_reg <= adc_data; // Output the original sample
                    valid_interpolated_data_reg <= 1'b1;
                end
            end else begin
                // If not interpolating, just pass through the ADC data (or hold last value)
                interpolated_data_reg <= adc_data;
                valid_interpolated_data_reg <= 1'b1; // Always valid when not interpolating (or based on pulse_detected)
            end
        end
    end

    assign interpolated_data = interpolated_data_reg;
    assign valid_interpolated_data = valid_interpolated_data_reg;

endmodule


