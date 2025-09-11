# XDC Constraints for xcau7p-fcva289-2-e (Artix UltraScale+)
# FCVA289 package - using only valid pins from the provided list

# Set default I/O standard
set_property IOSTANDARD LVCMOS18 [get_ports *]

# Clock pin
set_property PACKAGE_PIN B8 [get_ports clk]

# Reset signal pin
set_property PACKAGE_PIN B13 [get_ports rst_n]

# Control signals pins
set_property PACKAGE_PIN D14 [get_ports integral_ready]

# ADC data bus [11:0] - 12 pins needed
set_property PACKAGE_PIN A15 [get_ports {adc_data[0]}]
set_property PACKAGE_PIN B15 [get_ports {adc_data[1]}]
set_property PACKAGE_PIN B12 [get_ports {adc_data[2]}]
set_property PACKAGE_PIN C12 [get_ports {adc_data[3]}]
set_property PACKAGE_PIN A14 [get_ports {adc_data[4]}]
set_property PACKAGE_PIN B14 [get_ports {adc_data[5]}]
set_property PACKAGE_PIN A10 [get_ports {adc_data[6]}]
set_property PACKAGE_PIN B10 [get_ports {adc_data[7]}]
set_property PACKAGE_PIN C13 [get_ports {adc_data[8]}]
set_property PACKAGE_PIN D13 [get_ports {adc_data[9]}]
set_property PACKAGE_PIN A11 [get_ports {adc_data[10]}]
set_property PACKAGE_PIN B11 [get_ports {adc_data[11]}]


# Integral value bus [31:0] - 32 pins needed
set_property PACKAGE_PIN C15 [get_ports {integral_value[0]}]
set_property PACKAGE_PIN D15 [get_ports {integral_value[1]}]
set_property PACKAGE_PIN D12 [get_ports {integral_value[2]}]
set_property PACKAGE_PIN D11 [get_ports {integral_value[3]}]
set_property PACKAGE_PIN D17 [get_ports {integral_value[4]}]
set_property PACKAGE_PIN E17 [get_ports {integral_value[5]}]
set_property PACKAGE_PIN D10 [get_ports {integral_value[6]}]
set_property PACKAGE_PIN E10 [get_ports {integral_value[7]}]
set_property PACKAGE_PIN D16 [get_ports {integral_value[8]}]
set_property PACKAGE_PIN E15 [get_ports {integral_value[9]}]
set_property PACKAGE_PIN E13 [get_ports {integral_value[10]}]
set_property PACKAGE_PIN E12 [get_ports {integral_value[11]}]
set_property PACKAGE_PIN F16 [get_ports {integral_value[12]}]
set_property PACKAGE_PIN G15 [get_ports {integral_value[13]}]
set_property PACKAGE_PIN G12 [get_ports {integral_value[14]}]
set_property PACKAGE_PIN H12 [get_ports {integral_value[15]}]
set_property PACKAGE_PIN B17 [get_ports {integral_value[16]}]
set_property PACKAGE_PIN C16 [get_ports {integral_value[17]}]
set_property PACKAGE_PIN G11 [get_ports {integral_value[18]}]
set_property PACKAGE_PIN H11 [get_ports {integral_value[19]}]
set_property PACKAGE_PIN A16 [get_ports {integral_value[20]}]
set_property PACKAGE_PIN B16 [get_ports {integral_value[21]}]
set_property PACKAGE_PIN G14 [get_ports {integral_value[22]}]
set_property PACKAGE_PIN H14 [get_ports {integral_value[23]}]
set_property PACKAGE_PIN H16 [get_ports {integral_value[24]}]
set_property PACKAGE_PIN H15 [get_ports {integral_value[25]}]
set_property PACKAGE_PIN K13 [get_ports {integral_value[26]}]
set_property PACKAGE_PIN K12 [get_ports {integral_value[27]}]
set_property PACKAGE_PIN G17 [get_ports {integral_value[28]}]
set_property PACKAGE_PIN H17 [get_ports {integral_value[29]}]
set_property PACKAGE_PIN J15 [get_ports {integral_value[30]}]
set_property PACKAGE_PIN K14 [get_ports {integral_value[31]}]

set_property DRIVE 12 [get_ports {integral_value[*]}]
set_property SLEW FAST [get_ports {integral_value[*]}]

# Clock constraint for timing analysis
# 100 MHz
# create_clock -period 10.000 -name sys_clk_pin [get_ports clk]
# 150 MHz
# create_clock -period 6.666 -name sys_clk_pin [get_ports clk]
# 166 MHz
# create_clock -period 6.000 -name sys_clk_pin [get_ports clk]
# 180 MHz
# create_clock -period 5.555 -name sys_clk_pin [get_ports clk]
# 200 MHz
create_clock -period 5.000 -name sys_clk_pin [get_ports clk]
# 250 MHz
# create_clock -period 4.000 -name sys_clk_pin [get_ports clk]
# 400 MHz
# create_clock -period 2.500 -name sys_clk_pin [get_ports clk]

## Input delays
#set_input_delay -clock sys_clk_pin -max 1.5 [get_ports {adc_data[*]}]
#set_input_delay -clock sys_clk_pin -min 0.5 [get_ports {adc_data[*]}]

#set_input_delay -clock sys_clk_pin -max 1.0 [get_ports rst_n]
#set_input_delay -clock sys_clk_pin -min 0.3 [get_ports rst_n]

#set_input_delay -clock sys_clk_pin -max 1.0 [get_ports interp_en]
#set_input_delay -clock sys_clk_pin -min 0.3 [get_ports interp_en]

## Output delays
#set_output_delay -clock sys_clk_pin -max 1.8 [get_ports {integral_value[*]}]
#set_output_delay -clock sys_clk_pin -min -0.3 [get_ports {integral_value[*]}]

#set_output_delay -clock sys_clk_pin -max 1.2 [get_ports {integral_ready}]
#set_output_delay -clock sys_clk_pin -min -0.2 [get_ports {integral_ready}]