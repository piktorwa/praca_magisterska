module pulse_detector (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Assuming 12-bit ADC data
    input  logic [11:0] prev_adc_data,
    input  logic [11:0] prev_prev_adc_data,
    output logic pulse_detected,
    output logic [1:0] pulse_state_out
);

    // Parameters for pulse detection (adjust as needed)
    // These thresholds are now relative to the baseline or noise floor
    parameter BASELINE_THRESHOLD = 12'd10; // A small value above zero to detect activity (e.g., 0.01V for 5V range)
    parameter RISING_EDGE_THRESHOLD = 12'd5; // Minimum difference between consecutive samples to detect a rising edge
    parameter FALLING_EDGE_THRESHOLD = 12'd5; // Minimum difference between consecutive samples to detect a falling edge

    logic [11:0] current_pulse_peak_val;

    // State machine for pulse detection
    typedef enum logic [1:0] {IDLE, RISING, PEAK_DETECTED, FALLING} pulse_state_t;
    pulse_state_t pulse_state;


    assign pulse_state_out = pulse_state;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pulse_detected <= 1'b0;
            current_pulse_peak_val <= 12'b0;
            pulse_state <= IDLE;
        end else begin            
            case (pulse_state)
                IDLE: begin
                    // Look for a significant rise from baseline
                    if (adc_data > BASELINE_THRESHOLD && prev_adc_data > BASELINE_THRESHOLD && prev_prev_adc_data > BASELINE_THRESHOLD) begin
                        if (prev_adc_data > (prev_prev_adc_data + RISING_EDGE_THRESHOLD) && adc_data > (prev_adc_data + RISING_EDGE_THRESHOLD)) begin
                            pulse_state <= RISING;
                            current_pulse_peak_val <= adc_data;
                            pulse_detected <= 1'b1;
                        end
                    end
                end

                RISING: begin
                    if (adc_data > current_pulse_peak_val) begin
                        current_pulse_peak_val <= adc_data;
                    end
                    // If data starts falling significantly, transition to PEAK_DETECTED
                    if (adc_data < (prev_adc_data - FALLING_EDGE_THRESHOLD)) begin
                        pulse_state <= PEAK_DETECTED;
                    end
                end

                PEAK_DETECTED: begin
                    // Continue updating peak if a higher value is found (e.g., for double peaks)
                    if (adc_data > current_pulse_peak_val) begin
                        current_pulse_peak_val <= adc_data;
                        pulse_state <= RISING; // Go back to rising if it starts rising again
                    end
                    // If data falls significantly below the peak and approaches baseline
                    if (adc_data < (prev_adc_data - FALLING_EDGE_THRESHOLD)) begin
                        pulse_state <= FALLING;
                    end
                end

                FALLING: begin
                    // If data drops below baseline threshold and pulse duration is sufficient
                    if (adc_data < BASELINE_THRESHOLD && prev_adc_data >= BASELINE_THRESHOLD) begin
                        pulse_state <= IDLE; // Reset state
                        pulse_detected <= 1'b0; // Default to not detected
                    end
                end
            endcase
        end
    end

endmodule


