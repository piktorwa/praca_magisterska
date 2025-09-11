module integral_calculator (
    input  logic clk,
    input  logic rst_n,
    input  logic [11:0] data_in, // Input data (e.g., processed_data from interpolator)
    input  logic [11:0] prev_data_in,
    input  logic integrate_en, // Enable integration
    output logic [31:0] integral_value, // Accumulated integral value
    output logic integral_ready // Signal indicating integral calculation is complete
);

    logic [31:0] integral_sum;
    logic integrate_en_d; // opóźniona wersja integrate_en
    logic [12:0] avg_sample; // (data_in + prev_data_in) / 2

    // średnia arytmetyczna (reguła trapezów)
    assign avg_sample = ( {1'b0, data_in} + {1'b0, prev_data_in} ) >>> 1;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integral_sum   <= 32'b0;
            integral_value <= 32'b0;
            integral_ready <= 1'b0;
            integrate_en_d <= 1'b0;
        end else begin
            integral_ready <= 1'b0; // domyślnie wygaszamy
            
            // integracja w trakcie integrate_en = 1
            if (integrate_en) begin
                integral_sum <= integral_sum + avg_sample;
            end

            // wykrycie zbocza opadającego integrate_en
            else if (integrate_en_d && !integrate_en) begin
                integral_value <= integral_sum;
                integral_ready <= 1'b1;   // wynik gotowy na 1 cykl
                integral_sum   <= 32'b0;  // przygotuj się na kolejną integrację
            end

            integrate_en_d <= integrate_en;
        end
    end

endmodule

