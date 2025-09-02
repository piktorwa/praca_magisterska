module top_module (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Input from ADC (12-bit)
    input  logic interp_en, // Input enabling interpolation
    output logic [15:0] processed_data, // Output after pulse detection and interpolation (12-bit)
    output logic [31:0] integral_value, // Output of the integral calculation
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic pulse_detected_i;
    logic [2:0] pulse_state;
    logic valid_interpolated_data_i;
    logic [15:0] interpolated_data;

    pulse_detector pd_inst (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .pulse_detected(pulse_detected_i),
        .pulse_state_out(pulse_state)
    );

    linear_interpolator li_inst (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .pulse_detected(pulse_detected_i),
        .interp_en(interp_en),
        .interpolated_data(interpolated_data),
        .valid_interpolated_data(valid_interpolated_data_i)
    );
    
    assign processed_data = interpolated_data;
    
    integral_calculator ic_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(interpolated_data),
        .integrate_en(valid_interpolated_data_i),
        .pulse_state(pulse_state),
        .integral_out(integral_value),
        .integral_ready(integral_ready)
    );

endmodule