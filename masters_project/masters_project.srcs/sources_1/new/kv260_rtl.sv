`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01.07.2025 20:15:02
// Design Name: 
// Module Name: kv260_rtl
// Project Name: 
// Target Devices: KV260
// Tool Versions: 
// Description: Poprawiony system detekcji pulsów i interpolacji liniowej
// 
// Dependencies: 
// 
// Revision:
// Revision 0.02 - Fixed critical issues
// Additional Comments: Naprawiono logikę buforowania, interpolację i zabezpieczenia
// 
//////////////////////////////////////////////////////////////////////////////////

// Real-time ADC Pulse Detection and Linear Interpolation Module
module pulse_detector_interpolator #(
    parameter ADC_WIDTH = 12,           // ADC bit width
    parameter INTERP_FACTOR = 4,        // Interpolation factor (4x upsampling)
    parameter THRESHOLD = 12'h051,      // Detection threshold (~0.2V for 12-bit, 5V range)
    parameter HYSTERESIS = 12'h020,     // Hysteresis for robust detection
    parameter DERIVATIVE_THRESH = 12'h010 // Minimum derivative for rising edge
)(
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic [ADC_WIDTH-1:0]    adc_data,
    input  logic                    adc_valid,
    
    output logic [ADC_WIDTH-1:0]    interp_data,
    output logic                    interp_valid,
    output logic                    pulse_detected,
    output logic                    rising_edge_detected
);

// Continuous sample pipeline (real-time streaming)
logic [ADC_WIDTH-1:0] samples[0:3];  // 4-sample sliding window
logic [3:0] sample_valid;

// Pulse detection signals
logic pulse_active;
logic above_threshold, below_hysteresis;
logic rising_edge;

// Interpolation control
logic [$clog2(INTERP_FACTOR)-1:0] interp_count;
logic interp_active;
logic [ADC_WIDTH-1:0] interp_start, interp_end;
logic signed [ADC_WIDTH:0] interp_diff;
logic [ADC_WIDTH+$clog2(INTERP_FACTOR)-1:0] interp_result;

// Output control
logic output_original;
logic output_interp;

//=============================================================================
// Real-time Sample Pipeline
//=============================================================================
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        samples <= '{default: '0};
        sample_valid <= 4'b0000;
    end else if (adc_valid) begin
        // Shift samples in real-time
        samples[3] <= samples[2];
        samples[2] <= samples[1]; 
        samples[1] <= samples[0];
        samples[0] <= adc_data;
        sample_valid <= {sample_valid[2:0], 1'b1};
    end
end

//=============================================================================
// Real-time Pulse Detection
//=============================================================================
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        pulse_active <= 1'b0;
        pulse_detected <= 1'b0;
    end else if (adc_valid && sample_valid[0]) begin
        above_threshold = (samples[0] > THRESHOLD);
        below_hysteresis = (samples[0] < (THRESHOLD - HYSTERESIS));
        
        // State-based pulse detection with hysteresis
        case (pulse_active)
            1'b0: begin // Not in pulse
                if (above_threshold) begin
                    pulse_active <= 1'b1;
                    pulse_detected <= 1'b1;
                end else begin
                    pulse_detected <= 1'b0;
                end
            end
            
            1'b1: begin // In pulse
                if (below_hysteresis) begin
                    pulse_active <= 1'b0;
                    pulse_detected <= 1'b0;
                end else begin
                    pulse_detected <= 1'b1;
                end
            end
        endcase
    end else begin
        pulse_detected <= pulse_detected; // Hold value when no new data
    end
end

//=============================================================================
// Real-time Rising Edge Detection  
//=============================================================================
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        rising_edge <= 1'b0;
        rising_edge_detected <= 1'b0;
    end else if (adc_valid && sample_valid[1] && pulse_active) begin
        // Detect significant rising edge during pulse
        rising_edge = (samples[0] > samples[1]) && 
                     ((samples[0] - samples[1]) > DERIVATIVE_THRESH) &&
                     (samples[1] > samples[2]); // Sustained rise
        rising_edge_detected <= rising_edge;
    end else begin
        rising_edge_detected <= 1'b0;
    end
end

//=============================================================================
// Real-time Interpolation Engine
//=============================================================================
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        interp_active <= 1'b0;
        interp_count <= '0;
        interp_start <= '0;
        interp_end <= '0;
        interp_diff <= '0;
    end else begin
        if (rising_edge_detected && !interp_active && sample_valid[2]) begin
            // Start interpolation between samples[2] and samples[1]
            interp_active <= 1'b1;
            interp_count <= 1; // Start at 1 (0 would be original sample)
            interp_start <= samples[2];
            interp_end <= samples[1];
            interp_diff <= signed'(samples[1]) - signed'(samples[2]);
        end else if (interp_active) begin
            if (interp_count < INTERP_FACTOR - 1) begin
                interp_count <= interp_count + 1;
            end else begin
                interp_active <= 1'b0;
                interp_count <= '0;
            end
        end
    end
end

// Real-time interpolation calculation
always_comb begin
    if (interp_active) begin
        // Linear interpolation: start + (diff * count) / INTERP_FACTOR
        interp_result = (interp_start << $clog2(INTERP_FACTOR)) + 
                       (interp_diff * interp_count);
    end else begin
        interp_result = '0;
    end
end

//=============================================================================
// Real-time Output Control
//=============================================================================
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        interp_data <= '0;
        interp_valid <= 1'b0;
        output_original <= 1'b0;
        output_interp <= 1'b0;
    end else begin
        // Default: pass through original ADC data
        output_original = adc_valid && !interp_active && !rising_edge_detected;
        output_interp = interp_active;
        
        if (output_original) begin
            interp_data <= adc_data;
            interp_valid <= 1'b1;
        end else if (output_interp) begin
            interp_data <= interp_result >> $clog2(INTERP_FACTOR);
            interp_valid <= 1'b1;
        end else begin
            interp_valid <= 1'b0;
        end
    end
end

//=============================================================================
// Debug/Monitoring Outputs (can be removed for synthesis)
//=============================================================================
`ifdef SIMULATION
always @(posedge clk) begin
    if (adc_valid) begin
        $display("ADC: %0d, Pulse: %b, Rising: %b, Interp: %b", 
                 adc_data, pulse_detected, rising_edge_detected, interp_active);
    end
end
`endif

endmodule