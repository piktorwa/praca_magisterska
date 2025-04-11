# Author: Witkor Pantak
# Date: 2025-03-27
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: This is the main file for the project. It will be used to run the project and call the other files.

import simulations as sim

def main():
    # Call the function to plot the PMT pulse and its samples
    #sim.plot_for_sample_pulse()

    # Call the function to plot the PMT pulse and its samples with ADC
    sim.worst_case_for_amplitudes()

if __name__ == "__main__":
    main()
