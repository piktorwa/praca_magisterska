`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 27.07.2025 16:16:33
// Design Name: 
// Module Name: tb_kv260_fixed
// Project Name: 
// Target Devices: KV260
// Tool Versions: 
// Description: Poprawiony testbench dla systemu detekcji pulsów
// 
// Dependencies: 
// 
// Revision:
// Revision 0.02 - Fixed reset timing and improved test coverage
// Additional Comments: Dodano testy zabezpieczeń i poprawiono timing
// 
//////////////////////////////////////////////////////////////////////////////////

// Testbench for Real-time ADC Pulse Detection and Linear Interpolation
module tb_pulse_detector_interpolator;

    // Parameters
    parameter ADC_WIDTH = 12;
    parameter INTERP_FACTOR = 4;
    parameter THRESHOLD = 12'h051;
    parameter HYSTERESIS = 12'h020;
    parameter DERIVATIVE_THRESH = 12'h010;
    parameter CLK_PERIOD = 10;  // 100MHz clock (10ns period)
    
    // Testbench signals
    logic                    clk;
    logic                    rst_n;
    logic [ADC_WIDTH-1:0]    adc_data;
    logic                    adc_valid;
    logic [ADC_WIDTH-1:0]    interp_data;
    logic                    interp_valid;
    logic                    pulse_detected;
    logic                    rising_edge_detected;
    
    // Test control
    integer sample_count;
    integer output_count;
    logic test_running;
    
    // File for output logging
    integer out_file;
    
    // Instantiate DUT
    pulse_detector_interpolator #(
        .ADC_WIDTH(ADC_WIDTH),
        .INTERP_FACTOR(INTERP_FACTOR),
        .THRESHOLD(THRESHOLD),
        .HYSTERESIS(HYSTERESIS),
        .DERIVATIVE_THRESH(DERIVATIVE_THRESH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data(adc_data),
        .adc_valid(adc_valid),
        .interp_data(interp_data),
        .interp_valid(interp_valid),
        .pulse_detected(pulse_detected),
        .rising_edge_detected(rising_edge_detected)
    );
    
    // Clock generation - continuous real-time clock
    always #(CLK_PERIOD/2) clk = ~clk;
    
    // Real-time output monitoring
    always @(posedge clk) begin
        if (interp_valid) begin
            output_count++;
            $display("T=%0t | Output[%0d]: %0d (0x%0h) | Pulse:%b | Rising:%b", 
                     $time, output_count, interp_data, interp_data, 
                     pulse_detected, rising_edge_detected);
            
            // Log to file
            $fwrite(out_file, "%0t,%0d,%0d,%b,%b\n", 
                    $time, output_count, interp_data, pulse_detected, rising_edge_detected);
        end
    end
    
    // Real-time ADC data generator
    always @(posedge clk) begin
        if (test_running && rst_n) begin
            adc_valid <= 1'b1;  // Continuous valid data (real-time ADC)
            sample_count++;
            
            // Generate realistic ADC data stream with embedded pulses
            case (sample_count)
                // Baseline noise (50-60 counts, ~0.12-0.15V)
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10: 
                    adc_data <= 12'h035 + ($urandom % 16);  // 53 ± 8
                
                // First pulse: Fast rise (2ns rise time simulation)
                11: adc_data <= 12'h040;  // Start rising
                12: adc_data <= 12'h080;  // Sharp rise
                13: adc_data <= 12'h180;  // Steep
                14: adc_data <= 12'h300;  // Peak
                15: adc_data <= 12'h280;  // Start falling
                16: adc_data <= 12'h200;  
                17: adc_data <= 12'h120;
                18: adc_data <= 12'h080;
                19: adc_data <= 12'h050;
                20, 21, 22, 23, 24: 
                    adc_data <= 12'h038 + ($urandom % 12);
                
                // Second pulse: Medium rise (10ns rise time simulation)
                25: adc_data <= 12'h045;
                26: adc_data <= 12'h060;
                27: adc_data <= 12'h090;
                28: adc_data <= 12'h0D0;
                29: adc_data <= 12'h120;
                30: adc_data <= 12'h180;
                31: adc_data <= 12'h200;
                32: adc_data <= 12'h400;  // Peak
                33: adc_data <= 12'h380;
                34: adc_data <= 12'h300;
                35: adc_data <= 12'h250;
                36: adc_data <= 12'h180;
                37: adc_data <= 12'h100;
                38: adc_data <= 12'h080;
                39: adc_data <= 12'h050;
                40, 41, 42, 43, 44, 45: 
                    adc_data <= 12'h040 + ($urandom % 16);
                
                // Third pulse: Slow rise (25ns rise time simulation)
                46: adc_data <= 12'h048;
                47: adc_data <= 12'h055;
                48: adc_data <= 12'h070;
                49: adc_data <= 12'h095;
                50: adc_data <= 12'h0C0;
                51: adc_data <= 12'h100;
                52: adc_data <= 12'h150;
                53: adc_data <= 12'h1B0;
                54: adc_data <= 12'h220;
                55: adc_data <= 12'h2A0;
                56: adc_data <= 12'h350;
                57: adc_data <= 12'h420;
                58: adc_data <= 12'h500;
                59: adc_data <= 12'h600;
                60: adc_data <= 12'h800;  // Peak
                61: adc_data <= 12'h780;
                62: adc_data <= 12'h680;
                63: adc_data <= 12'h580;
                64: adc_data <= 12'h450;
                65: adc_data <= 12'h320;
                66: adc_data <= 12'h200;
                67: adc_data <= 12'h120;
                68: adc_data <= 12'h080;
                69: adc_data <= 12'h050;
                70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80: 
                    adc_data <= 12'h042 + ($urandom % 14);
                
                // Large amplitude pulse (approaching 5V)
                81: adc_data <= 12'h050;
                82: adc_data <= 12'h080;
                83: adc_data <= 12'h150;
                84: adc_data <= 12'h300;
                85: adc_data <= 12'h600;
                86: adc_data <= 12'h900;
                87: adc_data <= 12'hC00;
                88: adc_data <= 12'hF00;  // Near max
                89: adc_data <= 12'hE00;
                90: adc_data <= 12'hB00;
                91: adc_data <= 12'h800;
                92: adc_data <= 12'h500;
                93: adc_data <= 12'h300;
                94: adc_data <= 12'h150;
                95: adc_data <= 12'h080;
                96, 97, 98, 99, 100: 
                    adc_data <= 12'h045 + ($urandom % 18);
                
                default: begin
                    if (sample_count > 100) begin
                        test_running <= 1'b0;
                        adc_valid <= 1'b0;
                        $display("\n=== Real-time ADC simulation complete ===");
                        $display("Total samples processed: %0d", sample_count);
                        $display("Total outputs generated: %0d", output_count);
                        $fclose(out_file);
                        #(CLK_PERIOD * 20);
                        $finish;
                    end else begin
                        // Continue baseline
                        adc_data <= 12'h040 + ($urandom % 20);
                    end
                end
            endcase
        end else begin
            adc_valid <= 1'b0;
        end
    end
    
    // Test control and initialization
    initial begin
        // Initialize
        clk = 0;
        rst_n = 0;
        adc_data = 0;
        adc_valid = 0;
        sample_count = 0;
        output_count = 0;
        test_running = 0;
        
        // Open output file
        out_file = $fopen("adc_output.csv", "w");
        $fwrite(out_file, "Time,Sample,Value,Pulse_Detected,Rising_Edge\n");
        
        // Reset sequence
        #(CLK_PERIOD * 3);
        rst_n = 1;
        #(CLK_PERIOD * 2);
        
        $display("=== Real-time ADC Pulse Detection Test Started ===");
        $display("ADC Parameters: %0d-bit, Threshold=0x%0h, Interp_Factor=%0d", 
                 ADC_WIDTH, THRESHOLD, INTERP_FACTOR);
        $display("Simulating continuous 100MHz ADC stream...\n");
        
        // Start real-time test
        test_running = 1;
        
        // Let it run (will stop automatically when sample_count > 100)
    end
    
    // Waveform dump
    initial begin
        $dumpfile("pulse_detector_realtime.vcd");
        $dumpvars(0, tb_pulse_detector_interpolator);
    end
    
    // Safety timeout
    initial begin
        #(CLK_PERIOD * 2000);
        $display("ERROR: Testbench timeout - possible hang!");
        $fclose(out_file);
        $finish;
    end
    
    // Performance monitoring
    always @(posedge clk) begin
        if (sample_count > 0 && (sample_count % 20 == 0)) begin
            $display("--- Progress: %0d samples processed ---", sample_count);
        end
    end

endmodule