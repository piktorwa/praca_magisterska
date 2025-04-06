# Author: Witkor Pantak
# Date: 2025-03-27
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: This is the main file for the project. It will be used to run the project and call the other files.

import matplotlib.pyplot as plt
import integral
import interpolation
import signal_generator as sg
import plot_signals as ps

def main():
    # Constants for PMT pulse
    A = 0.6
    sigma = 3.0 * 10**(-9)
    tau = 9.0 * 10**(-9)

    start_time = -10 * 10**(-9)
    stop_time = 15 * 10**(-9)
    time_step = 0.001 * 10**(-9)

    # Samples for PMT pulse
    time_arr, value_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)
    
    sample_sizes = [8, 16, 32]

    # Dictionary to store all samples and interpolations
    samples = {
        'ideal': {},
        '8bit': {},
        '12bit': {}
    }
    
    linear_interpolations = {
        'ideal': {},
        '8bit': {},
        '12bit': {}
    }

    cubic_spline_interpolations = {
        'ideal': {},
        '8bit': {},
        '12bit': {}
    }
    
    # Generate all samples and interpolations
    for num_samples in sample_sizes:
        # Generate samples
        samples['ideal'][num_samples] = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
        samples['8bit'][num_samples] = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, 8)
        samples['12bit'][num_samples] = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, 12)
        
        # Generate linear interpolations
        linear_interpolations['ideal'][num_samples] = interpolation.linear_interpolation(*samples['ideal'][num_samples])
        linear_interpolations['8bit'][num_samples] = interpolation.linear_interpolation(*samples['8bit'][num_samples])
        linear_interpolations['12bit'][num_samples] = interpolation.linear_interpolation(*samples['12bit'][num_samples])

        # Generate cubic spline interpolations
        cubic_spline_interpolations['ideal'][num_samples] = interpolation.cubic_spline_interpolation(*samples['ideal'][num_samples])
        cubic_spline_interpolations['8bit'][num_samples] = interpolation.cubic_spline_interpolation(*samples['8bit'][num_samples])
        cubic_spline_interpolations['12bit'][num_samples] = interpolation.cubic_spline_interpolation(*samples['12bit'][num_samples])
    
    # Plot sampled signals
    # For ideal sampling
    t_samples_list_ideal = [samples['ideal'][size][0] for size in sample_sizes]
    y_samples_list_ideal = [samples['ideal'][size][1] for size in sample_sizes]
    sample_labels = [f"{size} próbek" for size in sample_sizes]
    
    ps.plot_sampled_signal(
        "Próbkowanie pulsu PMT", 
        time_arr, value_arr, 
        t_samples_list_ideal, y_samples_list_ideal, 
        sample_labels, 1
    )
    
    # For 8-bit ADC
    t_samples_list_8bit = [samples['8bit'][size][0] for size in sample_sizes]
    y_samples_list_8bit = [samples['8bit'][size][1] for size in sample_sizes]
    
    ps.plot_sampled_signal(
        "Próbkowanie ADC 8-bit", 
        time_arr, value_arr, 
        t_samples_list_8bit, y_samples_list_8bit, 
        sample_labels, 2
    )
    
    # For 12-bit ADC
    t_samples_list_12bit = [samples['12bit'][size][0] for size in sample_sizes]
    y_samples_list_12bit = [samples['12bit'][size][1] for size in sample_sizes]
    
    ps.plot_sampled_signal(
        "Próbkowanie ADC 12-bit", 
        time_arr, value_arr, 
        t_samples_list_12bit, y_samples_list_12bit, 
        sample_labels, 3
    )
    
    # Plot linear interpolated signals
    fig_num = 4
    for adc_type in ['ideal', '8bit', '12bit']:
        adc_label = {
            'ideal': 'idealne',
            '8bit': 'ADC 8-bit',
            '12bit': 'ADC 12-bit'
        }[adc_type]
        
        for num_samples in sample_sizes:
            t_samples, y_samples = samples[adc_type][num_samples]
            t_interp, y_interp = linear_interpolations[adc_type][num_samples]
            
            ps.plot_interpolated_signal(
                f"Interpolacja liniowa - {num_samples} próbek ({adc_label})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{num_samples} próbek",
                fig_num
            )
            fig_num += 1

    # Plot cubic spline interpolated signals
    for adc_type in ['ideal', '8bit', '12bit']:
        adc_label = {
            'ideal': 'idealne',
            '8bit': 'ADC 8-bit',
            '12bit': 'ADC 12-bit'
        }[adc_type]
        
        for num_samples in sample_sizes:
            t_samples, y_samples = samples[adc_type][num_samples]
            t_interp, y_interp = cubic_spline_interpolations[adc_type][num_samples]
            
            ps.plot_interpolated_signal(
                f"Interpolacja cubic spline - {num_samples} próbek ({adc_label})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{num_samples} próbek",
                fig_num
            )
            fig_num += 1

    # Integral calculation
    reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, start_time, stop_time)
    print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
    print(f"Oszacowany błąd scipy: {reference_error:.6e}")

    # Table header
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Próbki", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    # Integral calculation for sampled signals - Rectangle method
    sampling_types = {
        'Regularne': 'ideal', 
        'ADC 8-bit': '8bit', 
        'ADC 12-bit': '12bit'
    }
    
    for num_samples in sample_sizes:
        for sample_label, sample_key in sampling_types.items():
            # Get samples
            t_samples, y_samples = samples[sample_key][num_samples]
            
            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_samples, y_samples)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        
        print("-"*85)
    
    # Integral calculation for linear interpolated signals
    print("\nInterpolacja liniowa")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Próbki", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)
    
    for num_samples in sample_sizes:
        for sample_label, sample_key in sampling_types.items():
            # Get interpolated samples
            t_interp, y_interp = linear_interpolations[sample_key][num_samples]
            
            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        
        print("-"*85)
    
    # Integral calculation for cubic spline interpolated signals
    print("\nInterpolacja cubic spline")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Próbki", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)
    
    for num_samples in sample_sizes:
        for sample_label, sample_key in sampling_types.items():
            # Get interpolated samples
            t_interp, y_interp = cubic_spline_interpolations[sample_key][num_samples]
            
            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        
        print("-"*85)
    plt.show()

if __name__ == "__main__":
    main()
