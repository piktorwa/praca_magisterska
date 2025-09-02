module pulse_detector (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] adc_data, // Assuming 12-bit ADC data
    output logic pulse_detected,
    output logic [2:0] pulse_state_out
);

    // Parameters for pulse detection (adjust as needed)
    // These thresholds are now relative to the baseline or noise floor
    parameter BASELINE_THRESHOLD = 12'd10; // A small value above zero to detect activity (e.g., 0.01V for 5V range)
    parameter RISING_EDGE_THRESHOLD = 12'd5; // Minimum difference between consecutive samples to detect a rising edge
    parameter FALLING_EDGE_THRESHOLD = 12'd5; // Minimum difference between consecutive samples to detect a falling edge
    parameter MIN_PULSE_DURATION = 10; // Minimum number of cycles for a valid pulse

    logic [11:0] prev_adc_data;
    logic [11:0] prev_prev_adc_data;
    logic in_pulse;
    logic [31:0] pulse_cycle_counter;
    logic [11:0] current_pulse_start_val;
    logic [11:0] current_pulse_peak_val;

    // State machine for pulse detection
    typedef enum logic [1:0] {IDLE, RISING, PEAK_DETECTED, FALLING} pulse_state_t;
    pulse_state_t pulse_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            in_pulse <= 1'b0;
            pulse_detected <= 1'b0;
            pulse_cycle_counter <= 32'b0;
            current_pulse_start_val <= 12'b0;
            current_pulse_peak_val <= 12'b0;
            prev_adc_data <= 12'b0;
            prev_prev_adc_data <= 12'b0;
            pulse_state <= IDLE;
        end else begin
            prev_prev_adc_data <= prev_adc_data;
            prev_adc_data <= adc_data;
            
            case (pulse_state)
                IDLE: begin
                    // Look for a significant rise from baseline
                    if (adc_data > (prev_adc_data + RISING_EDGE_THRESHOLD) && adc_data > BASELINE_THRESHOLD) begin
                        pulse_state <= RISING;
                        current_pulse_start_val <= prev_adc_data; // Value just before significant rise
                        current_pulse_peak_val <= adc_data;
                        pulse_cycle_counter <= 32'b0;
                        in_pulse <= 1'b1;
                        pulse_detected <= 1'b1;
                    end
                end

                RISING: begin
                    pulse_cycle_counter <= pulse_cycle_counter + 1;
                    if (adc_data > current_pulse_peak_val) begin
                        current_pulse_peak_val <= adc_data;
                    end
                    // If data starts falling significantly, transition to PEAK_DETECTED
                    if (adc_data < (prev_adc_data - FALLING_EDGE_THRESHOLD)) begin
                        pulse_state <= PEAK_DETECTED;
                    end
                end

                PEAK_DETECTED: begin
                    pulse_cycle_counter <= pulse_cycle_counter + 1;
                    // Continue updating peak if a higher value is found (e.g., for double peaks)
                    if (adc_data > current_pulse_peak_val) begin
                        current_pulse_peak_val <= adc_data;
                        pulse_state <= RISING; // Go back to rising if it starts rising again
                    end
                    // If data falls significantly below the peak and approaches baseline
                    if (adc_data < (prev_adc_data - FALLING_EDGE_THRESHOLD) && adc_data < BASELINE_THRESHOLD) begin
                        pulse_state <= FALLING;
                        pulse_state_out <= FALLING;
                    end
                end

                FALLING: begin
                    pulse_cycle_counter <= pulse_cycle_counter + 1;
                    // If data drops below baseline threshold and pulse duration is sufficient
                    if (adc_data < BASELINE_THRESHOLD && prev_adc_data >= BASELINE_THRESHOLD) begin
                        in_pulse <= 1'b0;
                        pulse_state_out <= IDLE;
                        pulse_state <= IDLE; // Reset state
                        pulse_detected <= 1'b0; // Default to not detected
                    end
                    // If it starts rising again, it might be a new pulse or noise, go back to IDLE or RISING
                    if (adc_data > (prev_adc_data + RISING_EDGE_THRESHOLD)) begin
                        in_pulse <= 1'b0;
                        pulse_state <= RISING; // Treat as noise or start of new pulse
                    end
                end
            endcase
        end
    end

endmodule


