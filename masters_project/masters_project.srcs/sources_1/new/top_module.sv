module top_module (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Input from ADC (12-bit)
    output logic [31:0] integral_value, // Output of the integral calculation
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic pulse_detected_i;
    logic [11:0] prev_adc_data;
    logic [11:0] prev_prev_adc_data;
    logic [1:0] pulse_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            prev_adc_data <= 12'b0;
            prev_prev_adc_data <= 12'b0;
        end else begin
            prev_prev_adc_data <= prev_adc_data;
            prev_adc_data <= adc_data;
        end
    end

    pulse_detector pd_inst (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .prev_adc_data(prev_adc_data),
        .prev_prev_adc_data(prev_prev_adc_data),
        .pulse_detected(pulse_detected_i),
        .pulse_state_out(pulse_state)
    );
    
    integral_calculator ic_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(prev_adc_data),
        .prev_data_in(prev_prev_adc_data),
        .integrate_en(pulse_detected_i),
        .integral_value(integral_value),
        .integral_ready(integral_ready)
    );

endmodule