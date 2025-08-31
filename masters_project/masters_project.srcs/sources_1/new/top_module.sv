module top_module (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Input from ADC (12-bit)
    output logic [11:0] processed_data, // Output after pulse detection and interpolation (12-bit)
    output logic [31:0] integral_value, // Output of the integral calculation
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic pulse_detected_i;
    logic [11:0] pulse_start_val_i;
    logic [11:0] pulse_peak_val_i;
    logic [31:0] pulse_duration_cycles_i;
    logic valid_interpolated_data_i;

    pulse_detector pd_inst (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .pulse_detected(pulse_detected_i),
        .pulse_start_val(pulse_start_val_i),
        .pulse_peak_val(pulse_peak_val_i),
        .pulse_duration_cycles(pulse_duration_cycles_i)
    );

    linear_interpolator li_inst (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .pulse_detected(pulse_detected_i),
        .pulse_start_val(pulse_start_val_i),
        .pulse_peak_val(pulse_peak_val_i),
        .pulse_duration_cycles(pulse_duration_cycles_i),
        .interpolated_data(processed_data),
        .valid_interpolated_data(valid_interpolated_data_i)
    );

    integral_calculator ic_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(processed_data),
        .integrate_en(valid_interpolated_data_i), // Enable integration when interpolated data is valid
        .integral_out(integral_value),
        .integral_ready(integral_ready) // New output signal
    );

endmodule

