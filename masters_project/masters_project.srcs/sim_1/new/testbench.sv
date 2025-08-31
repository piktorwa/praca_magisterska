`timescale 1ns / 1ps

module testbench;

    // Parameters
    parameter real tr_val = 10.0 * 1e-9; // 10 ns
    parameter real sigma_val = tr_val / 1.69; // Calculate sigma based on tr
    parameter real CLK_PERIOD_REAL = 2.9585798816568047; // Period for 2 samples per sigma, calculated from tr_val=10ns
    parameter CLK_PERIOD = CLK_PERIOD_REAL * 1ns; // Assign with time unit

    // Signals
    logic clk;
    logic rst_n;
    logic [11:0] adc_data; // Adjusted to 12-bit ADC data
    logic [11:0] processed_data; // Adjusted to 12-bit processed data
    logic [31:0] integral_value;
    logic pulse_detected_displayed;
    real pulse_detection_time;
    real integral_ready_time;

    // Variables for non-interpolated integral and duration (moved to module scope)
    longint non_interp_integral_sum = 0;
    real non_interp_start_time = 0.0;
    real non_interp_end_time = 0.0;

    // Variables for interpolated integral and duration (already in module scope)
    longint interp_integral_sum = 0;
    real interp_start_time = 0.0;
    real interp_end_time = 0.0;
    logic first_interp_sample = 1;

    // Variables for integral verification
    longint tb_non_interp_integral_sum = 0;
    longint tb_interp_integral_sum = 0;

    // Instantiate the Device Under Test (DUT)
    top_module dut (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .processed_data(processed_data),
        .integral_value(integral_value)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD / 2) clk = ~clk;
    end

    // Function to generate pulse value based on the formula
    function real get_pulse_value(real t, real A, real sigma, real tau);
        real C;
        real th;
        real val;

        C = $exp(-0.5 * (sigma * tau) * (sigma * tau));
        th = 2 * sigma * sigma / tau;

        if (t <= th) begin
            val = A * $exp(-0.5 * (t / sigma) * (t / sigma));
        end else begin
            val = (A / C) * $exp(-1.0 * (t / tau));
        end
        return val;
    endfunction

    // Reset generation and test stimulus
    initial begin
        // Use parameters defined at the top of the module
        real A = tr_val * 1e8; // Amplitude (V) - original definition
        real sigma = sigma_val; // Use the calculated sigma_val
        real tau = 3 * sigma; // Related to exponential decay (ns)
        real time_step = sigma / 2; // Time per clock cycle in ns

        // Calculate number of samples based on 8 sigmas before amplitude and 24 sigmas after
        // with 2 samples per sigma.
        real total_duration = 26.0 * sigma; // Total duration in ns (26 sigmas as requested by user) 
        int num_samples = $rtoi(total_duration / time_step); // Number of samples

        real current_time_local = -13.0 * sigma; // Start 13 sigmas before the center for a 26 sigma total duration

        rst_n = 0;
        adc_data = 0;
        #(CLK_PERIOD * 2) rst_n = 1; // Assert reset for 2 clock cycles

        // Test Case 1: No pulse (baseline noise)
        $display("\n--- Test Case 1: No pulse (baseline noise) ---");
        for (int i = 0; i < 20; i++) begin
            adc_data = 12'd5 + $urandom_range(0, 5); // Simulate some noise around baseline
            #(CLK_PERIOD);
        end

        // Test Case 2: Single pulse with new definition
        $display("\n--- Test Case 2: Single pulse (new definition) ---");

        non_interp_start_time = $realtime;

        // Start below baseline, then generate pulse
        adc_data = 12'd5; // Start with a small non-zero baseline to ensure ADC data is not always zero
        #(CLK_PERIOD * 5);

        for (int i = 0; i < num_samples; i++) begin
            real pulse_val = get_pulse_value(current_time_local, A, sigma, tau);
            // Scale pulse_val (0-5V) to 12-bit ADC data (0-4095)
            // Assuming 5V max input for ADC, so 5V maps to 12'hFFF
            adc_data = $rtoi((pulse_val / 5.0) * 4095.0);
            $display("Time: %0t, current_time: %0f, pulse_val: %0f, scaled_adc_data_real: %0f, adc_data: %h", $time, current_time_local, pulse_val, (pulse_val / 5.0) * 4095.0, adc_data);
            
            // Accumulate for non-interpolated integral (for verification)
            tb_non_interp_integral_sum += adc_data;

            #(CLK_PERIOD);
            current_time_local = current_time_local + time_step;
        end
        adc_data = 12'd0; // End of pulse
        #(CLK_PERIOD * 10);

        non_interp_end_time = $realtime;


        // End simulation
        $display("\n--- Simulation Complete ---");
        $finish;
    end

    // Monitor outputs (optional, for debugging)
    always @(posedge dut.pd_inst.pulse_detected) begin
        if (!pulse_detected_displayed) begin
            $display("DEBUG: Pulse Detected! Time: %0t, State: %s", $time, dut.pd_inst.pulse_state.name());
            pulse_detected_displayed = 1'b1;
            pulse_detection_time = $realtime;
        end
    end

    always @(negedge dut.pd_inst.pulse_detected) begin
        pulse_detected_displayed = 1'b0;
    end

    always @(posedge clk) begin

        // Debugging: Check if valid_interpolated_data is active
        if (dut.li_inst.valid_interpolated_data) begin
            $display("DEBUG: Valid Interpolated Data! Time: %0t, Processed_Data: %h", $time, processed_data);
            if (first_interp_sample) begin
                interp_start_time = $realtime;
                first_interp_sample = 0;
            end
            tb_interp_integral_sum += processed_data; // Accumulate for interpolated integral (for verification)
            interp_end_time = $realtime;

            $display("Time: %0t, ADC_Data: %h, Processed_Data: %h, Integral_Value: %h, Pulse_Detected: %b, Valid_Interpolated: %b, Pulse_State: %s",
                     $time, adc_data, processed_data, integral_value, dut.pd_inst.pulse_detected, dut.li_inst.valid_interpolated_data, dut.pd_inst.pulse_state.name());
        end
    end

    always @(posedge dut.integral_ready) begin
        integral_ready_time = $realtime;
        $display("Time: %0t - INTEGRAL READY! Integral value: %0d (Decimal), %0h (Hexadecimal)", $time, integral_value, integral_value);
        $display("Time from Pulse Detection to Integral Ready: %0f ns", (integral_ready_time - pulse_detection_time) / 1ns);
    end

    final begin
        $display("\n--- Interpolated Data Results ---");
        $display("Non-interpolated Integral (TB): %0e V*s", tb_non_interp_integral_sum * (5.0 / 4095.0) * CLK_PERIOD_REAL * 1e-9);
        $display("Interpolated Integral (TB): %0e V*s", tb_interp_integral_sum * (5.0 / 4095.0) * CLK_PERIOD_REAL * 1e-9);
        $display("Interpolated Integral (DUT): %0e V*s", integral_value * (5.0 / 4095.0) * CLK_PERIOD_REAL * 1e-9); // Display DUT's final integral
        $display("Interpolated Duration: %0f ns", (interp_end_time - interp_start_time) / 1ns);
    end

endmodule


