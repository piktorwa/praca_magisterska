# Author: Witkor Pantak
# Date: 2025-04-10
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: File contains functions that simulate some processes and generate signals.

import matplotlib.pyplot as plt
import integral
import interpolation
import signal_generator as sg
import plot_signals as ps
import numpy as np
import pandas as pd

poly_degree = 20  # Degree of polynomial for interpolation
integral_window_start = -20 * 10**(-9)
integral_window_stop = 80 * 10**(-9)

# Restrict samples to integration window
def restrict_to_window(t, y):
    mask = (t >= integral_window_start) & (t <= integral_window_stop)
    return t[mask], y[mask]

def plot_for_sample_pulse():
    # Constants for PMT pulse
    tr = 10.0 * 10**(-9) # pulse rise time
    A = 1.0 # amplitude of the pulse in V
    sigma = tr / 1.69 # related to rise time
    tau = 3 * sigma # related to fall time

    start_time = -8 * sigma
    stop_time = 6 * tau
    time_step = 0.01 * 10**(-9)

    # Samples for PMT pulse
    time_arr, value_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)
    
    # Number of samples - based on samples per sigma
    sample_sizes = []
    samples_per_sigma = [1, 2, 3]
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time - start_time) / sigma))
        sample_sizes.append(num_samples)

    phase = sigma * 0/360 # phase shift in seconds
    start_time += phase
    stop_time += phase

    # Dictionary to store all samples and interpolations
    samples = {
        'n-bit': {},
        '8bit': {},
        '12bit': {}
    }
    
    linear_interpolations = {
        'n-bit': {},
        '8bit': {},
        '12bit': {}
    }

    cubic_spline_interpolations = {
        'n-bit': {},
        '8bit': {},
        '12bit': {}
    }

    polynomial_interpolations = {
        'n-bit': {},
        '8bit': {},
        '12bit': {}
    }
    
    # Generate all samples and interpolations
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time - start_time) / sigma))
        # Generate samples
        samples['n-bit'][sps] = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
        samples['8bit'][sps] = sg.sample_signal_ADC_n_bit_ver_2(*samples['n-bit'][sps], 8)
        samples['12bit'][sps] = sg.sample_signal_ADC_n_bit_ver_2(*samples['n-bit'][sps], 12)

        # Generate linear interpolations
        linear_interpolations['n-bit'][sps] = interpolation.linear_interpolation(*samples['n-bit'][sps])
        linear_interpolations['8bit'][sps] = interpolation.linear_interpolation(*samples['8bit'][sps])
        linear_interpolations['12bit'][sps] = interpolation.linear_interpolation(*samples['12bit'][sps])

        linear_interpolations['n-bit'][sps] = restrict_to_window(np.array(linear_interpolations['n-bit'][sps][0]), np.array(linear_interpolations['n-bit'][sps][1]))
        linear_interpolations['8bit'][sps] = restrict_to_window(np.array(linear_interpolations['8bit'][sps][0]), np.array(linear_interpolations['8bit'][sps][1]))
        linear_interpolations['12bit'][sps] = restrict_to_window(np.array(linear_interpolations['12bit'][sps][0]), np.array(linear_interpolations['12bit'][sps][1]))

        # Generate cubic spline interpolations
        cubic_spline_interpolations['n-bit'][sps] = interpolation.cubic_spline_interpolation(*samples['n-bit'][sps])
        cubic_spline_interpolations['8bit'][sps] = interpolation.cubic_spline_interpolation(*samples['8bit'][sps])
        cubic_spline_interpolations['12bit'][sps] = interpolation.cubic_spline_interpolation(*samples['12bit'][sps])

        cubic_spline_interpolations['n-bit'][sps] = restrict_to_window(np.array(cubic_spline_interpolations['n-bit'][sps][0]), np.array(cubic_spline_interpolations['n-bit'][sps][1]))
        cubic_spline_interpolations['8bit'][sps] = restrict_to_window(np.array(cubic_spline_interpolations['8bit'][sps][0]), np.array(cubic_spline_interpolations['8bit'][sps][1]))
        cubic_spline_interpolations['12bit'][sps] = restrict_to_window(np.array(cubic_spline_interpolations['12bit'][sps][0]), np.array(cubic_spline_interpolations['12bit'][sps][1]))

        # Generate polynomial interpolations
        polynomial_interpolations['n-bit'][sps] = interpolation.polynomial_interpolation(samples['n-bit'][sps][0], samples['n-bit'][sps][1], poly_degree)
        polynomial_interpolations['8bit'][sps] = interpolation.polynomial_interpolation(samples['8bit'][sps][0], samples['8bit'][sps][1], poly_degree)
        polynomial_interpolations['12bit'][sps] = interpolation.polynomial_interpolation(samples['12bit'][sps][0], samples['12bit'][sps][1], poly_degree)

        polynomial_interpolations['n-bit'][sps] = restrict_to_window(np.array(polynomial_interpolations['n-bit'][sps][0]), np.array(polynomial_interpolations['n-bit'][sps][1]))
        polynomial_interpolations['8bit'][sps] = restrict_to_window(np.array(polynomial_interpolations['8bit'][sps][0]), np.array(polynomial_interpolations['8bit'][sps][1]))
        polynomial_interpolations['12bit'][sps] = restrict_to_window(np.array(polynomial_interpolations['12bit'][sps][0]), np.array(polynomial_interpolations['12bit'][sps][1]))

        samples['n-bit'][sps] = restrict_to_window(np.array(samples['n-bit'][sps][0]), np.array(samples['n-bit'][sps][1]))
        samples['8bit'][sps] = restrict_to_window(np.array(samples['8bit'][sps][0]), np.array(samples['8bit'][sps][1]))
        samples['12bit'][sps] = restrict_to_window(np.array(samples['12bit'][sps][0]), np.array(samples['12bit'][sps][1]))

    # Plot sampled signals
        
    # --- Plot 1: Only the reference pulse ---
    plt.figure(1)
    plt.plot(np.array(time_arr)*1e9, value_arr, label="puls PMT")
    plt.xlabel("Czas [ns]", fontsize=28)
    plt.ylabel("Amplituda [V]", fontsize=28)
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.title("Referencyjny puls PMT", fontsize=28)
    plt.legend(fontsize=22)
    plt.grid()

    # --- Plot 2+: Pulse with overlaid samples for each ADC type and sample size ---
    fig_num = 2
    adc_types = ['n-bit', '8bit', '12bit']
    adc_labels = {
        'n-bit': 'ADC ∞-bit',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    for adc_type in adc_types:
        for sps in samples_per_sigma:
            t_samples, y_samples = samples[adc_type][sps]
            plt.figure(fig_num)
            plt.plot(np.array(time_arr)*1e9, value_arr, label="PMT pulse")
            plt.plot(np.array(t_samples)*1e9, y_samples, 'ro', linestyle='', label=f"{sps} SPS")
            plt.xlabel("Czas [ns]", fontsize=28)
            plt.ylabel("Amplituda [V]", fontsize=28)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
            plt.title(f"Próbki {adc_labels[adc_type]} - {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę", fontsize=28)
            plt.legend(fontsize=22)
            plt.grid()
            fig_num += 1
    
    # For ideal sampling
    t_samples_list_ideal = [samples['n-bit'][sps][0] for sps in samples_per_sigma]
    y_samples_list_ideal = [samples['n-bit'][sps][1] for sps in samples_per_sigma]
    sample_labels = [f"{sps} SPS" for sps in samples_per_sigma]
    ps.plot_sampled_signal(
        "Próbkowanie pulsu PMT", 
        time_arr, value_arr, 
        t_samples_list_ideal, y_samples_list_ideal, 
        sample_labels, fig_num
    )
    fig_num += 1

    # For 8-bit ADC
    t_samples_list_8bit = [samples['8bit'][sps][0] for sps in samples_per_sigma]
    y_samples_list_8bit = [samples['8bit'][sps][1] for sps in samples_per_sigma]

    ps.plot_sampled_signal(
        "Próbkowanie ADC 8-bit", 
        time_arr, value_arr, 
        t_samples_list_8bit, y_samples_list_8bit, 
        sample_labels, fig_num
    )
    fig_num += 1

    # For 12-bit ADC
    t_samples_list_12bit = [samples['12bit'][sps][0] for sps in samples_per_sigma]
    y_samples_list_12bit = [samples['12bit'][sps][1] for sps in samples_per_sigma]

    ps.plot_sampled_signal(
        "Próbkowanie ADC 12-bit", 
        time_arr, value_arr, 
        t_samples_list_12bit, y_samples_list_12bit, 
        sample_labels, fig_num
    )
    fig_num += 1

    # Plot linear interpolated signals
    for adc_type in adc_types:
        for sps in samples_per_sigma:
            t_samples, y_samples = samples[adc_type][sps]
            t_interp, y_interp = linear_interpolations[adc_type][sps]

            ps.plot_interpolated_signal(
                f"Interpolacja liniowa - {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę ({adc_labels[adc_type]})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{sps} SPS",
                fig_num,
                "Interpolacja liniowa"
            )
            fig_num += 1

    # Plot cubic spline interpolated signals
    for adc_type in adc_types:        
        for sps in samples_per_sigma:
            t_samples, y_samples = samples[adc_type][sps]
            t_interp, y_interp = cubic_spline_interpolations[adc_type][sps]

            ps.plot_interpolated_signal(
                f"Interpolacja cubic spline - {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę ({adc_labels[adc_type]})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{sps} SPS",
                fig_num,
                "Interpolacja cubic spline"
            )
            fig_num += 1

    # Plot polynomial interpolated signals
    for adc_type in adc_types:
        for sps in samples_per_sigma:
            t_samples, y_samples = samples[adc_type][sps]
            t_interp, y_interp = polynomial_interpolations[adc_type][sps]

            ps.plot_interpolated_signal(
                f"Interpolacja wielomianowa {poly_degree} st. - {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę ({adc_labels[adc_type]})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{sps} SPS",
                fig_num,
                f"Interpolacja wielomianowa {poly_degree} st."
            )
            fig_num += 1

    # Export for samples_per_sigma = 1
    sps = 1

    # Raw samples
    t_raw, y_raw = samples['n-bit'][sps]

    # Linear interpolation
    t_linear, y_linear = linear_interpolations['n-bit'][sps]

    # Cubic spline interpolation
    t_cubic, y_cubic = cubic_spline_interpolations['n-bit'][sps]

    # Prepare DataFrame with aligned lengths (longest sample set)
    max_len = max(len(t_raw), len(t_linear), len(t_cubic))
    def pad(arr, length):
        return np.pad(arr, (0, length - len(arr)), constant_values=np.nan)

    df = pd.DataFrame({
        't_raw [s]': pad(t_raw, max_len),
        'y_raw [V]': pad(y_raw, max_len),
        't_linear [s]': pad(t_linear, max_len),
        'y_linear [V]': pad(y_linear, max_len),
        't_cubic [s]': pad(t_cubic, max_len),
        'y_cubic [V]': pad(y_cubic, max_len),
    })

    df.to_excel('samples_export.xlsx', sheet_name='samples', index=False)

    # Integral calculation
    reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)
    print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
    print(f"Oszacowany błąd scipy: {reference_error:.6e}")

    # Table header
    print("\nBez interpolacji")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    # Integral calculation for sampled signals - Rectangle method
    sampling_types = {
        'ADC n-bit': 'n-bit', 
        'ADC 8-bit': '8bit', 
        'ADC 12-bit': '12bit'
    }

    for sps in samples_per_sigma:
        for sample_label, sample_key in sampling_types.items():
            # Get samples
            t_samples, y_samples = samples[sample_key][sps]

            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_samples, y_samples)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.3e} | {:.3e} | {:^15.5f}".format(
                sps, sample_label, integral_val, abs_err, rel_err))

        print("-"*85)
    
    # Integral calculation for linear interpolated signals
    print("\nInterpolacja liniowa")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    for sps in samples_per_sigma:
        for sample_label, sample_key in sampling_types.items():
            # Get interpolated samples
            t_interp, y_interp = linear_interpolations[sample_key][sps]

            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.3e} | {:.3e} | {:^15.5f}".format(
                sps, sample_label, integral_val, abs_err, rel_err))

        print("-"*85)
    
    # Integral calculation for cubic spline interpolated signals
    print("\nInterpolacja cubic spline")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    for sps in samples_per_sigma:
        for sample_label, sample_key in sampling_types.items():
            # Get interpolated samples
            t_interp, y_interp = cubic_spline_interpolations[sample_key][sps]

            # Calculate integral
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)

            # Calculate errors
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.3e} | {:.3e} | {:^15.5f}".format(
                sps, sample_label, integral_val, abs_err, rel_err))

        print("-"*85)
    
    # Integral calculation for polynomial interpolated signals
    print("\nInterpolacja wielomianowa st. {}".format(poly_degree))
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    for sps in samples_per_sigma:
        for sample_label, sample_key in sampling_types.items():
            t_interp, y_interp = polynomial_interpolations[sample_key][sps]
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            print("{:^10} | {:^20} | {:.3e} | {:.3e} | {:^15.5f}".format(
                sps, sample_label, integral_val, abs_err, rel_err))
        print("-"*85)

    # Plot bar charts of relative errors
    rel_errors = {
        'n-bit': {},
        '8bit': {},
        '12bit': {}
    }
    for adc_key in rel_errors:
        rel_errors[adc_key] = {}
        for sps in samples_per_sigma:
            # Raw
            t_raw, y_raw = samples[adc_key][sps]
            integral_raw = integral.integrate_rectangle_method(t_raw, y_raw)
            _, rel_err_raw = integral.calculate_error(integral_raw, reference_result)

            # Linear
            t_linear, y_linear = linear_interpolations[adc_key][sps]
            integral_linear = integral.integrate_rectangle_method(t_linear, y_linear)
            _, rel_err_linear = integral.calculate_error(integral_linear, reference_result)

            # Polynomial
            t_poly, y_poly = polynomial_interpolations[adc_key][sps]
            integral_poly = integral.integrate_rectangle_method(t_poly, y_poly)
            _, rel_err_poly = integral.calculate_error(integral_poly, reference_result)

            # Cubic spline
            t_cubic, y_cubic = cubic_spline_interpolations[adc_key][sps]
            integral_cubic = integral.integrate_rectangle_method(t_cubic, y_cubic)
            _, rel_err_cubic = integral.calculate_error(integral_cubic, reference_result)

            rel_errors[adc_key][sps] = [rel_err_raw, rel_err_linear, rel_err_poly, rel_err_cubic]
    
    interp_labels = ['Bez interpolacji', 'Interpolacja liniowa', f'Interpolacja wielomianowa {poly_degree} st.', 'Interpolacja cubic spline']
    interp_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    bar_width = 0.18
    x = np.arange(len(samples_per_sigma))  # [0, 1, 2] for SPS=1,2,3

    for adc_key, adc_label in adc_labels.items():
        plt.figure(figsize=(10, 6))
        # For each interpolation, plot bars for all SPS
        for i, (interp_label, color) in enumerate(zip(interp_labels, interp_colors)):
            # Get errors for all SPS for this interpolation
            y = [rel_errors[adc_key][sps][i] for sps in samples_per_sigma]
            plt.bar(x + i*bar_width, y, width=bar_width, color=color, label=interp_label, zorder=2)
        plt.xlabel("Liczba próbek na sigmę", fontsize=28)
        plt.ylabel("Błąd względny [%]", fontsize=28)
        plt.title(f"Błąd względny dla {adc_label}", fontsize=28)
        plt.xticks(x + 1.5*bar_width, samples_per_sigma, fontsize=22)  # Center group labels
        plt.yticks(fontsize=22)
        plt.grid(axis='y', linestyle='-', alpha=0.7, zorder=1)
        plt.legend(fontsize=22)
        plt.tight_layout()
    plt.show()

def worst_case_for_amplitudes():
    # Test parameters
    amplitudes = [0.1, 1, 5]
    tr = 10 * 10**(-9)
    sigma = tr / 1.69
    tau = 3 * sigma
    start_time_orig = -8 * sigma
    stop_time_orig = 6 * tau
    samples_per_sigma = [1, 2, 3, 4]
    phase_step = 1
    phases = range(0, 360, phase_step)

    error_count = 0  # Error counter

    # Dictionaries to store results
    interp_names = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline',
        'poly': f'Interpolacja wielomianowa {poly_degree} st.'
    }
    adc_names = {
        'n-bit': 'ADC ∞-bit',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    # Main loop over different rise times
    for A in amplitudes:

        # Structure to store maximum errors
        max_errors = {
            interp: {
                adc: {sps: {'max_error': 0, 'phase': 0} for sps in samples_per_sigma}
                for adc in adc_names
            }
            for interp in interp_names
        }

        print(f"\nTesting amplitude: {A} V")

        reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)
        print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
        print(f"Oszacowany błąd scipy: {reference_error:.6e}")

        # Loop through different phase shifts (in degrees)
        for phase_deg in phases:
            start_time = start_time_orig + sigma * phase_deg / 360
            stop_time = stop_time_orig + sigma * phase_deg / 360
            # Loop through different sample sizes
            for sps in samples_per_sigma:
                num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
                try:
                    # Raw samples
                    t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
                    t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
                    t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

                    # Interpolations
                    # Linear interpolation
                    t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
                    t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
                    t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

                    t_linear_ideal, y_linear_ideal = restrict_to_window(np.array(t_linear_ideal), np.array(y_linear_ideal))
                    t_linear_8bit, y_linear_8bit = restrict_to_window(np.array(t_linear_8bit), np.array(y_linear_8bit))
                    t_linear_12bit, y_linear_12bit = restrict_to_window(np.array(t_linear_12bit), np.array(y_linear_12bit))

                    # Cubic
                    t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                    t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                    t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

                    t_cubic_ideal, y_cubic_ideal = restrict_to_window(np.array(t_cubic_ideal), np.array(y_cubic_ideal))
                    t_cubic_8bit, y_cubic_8bit = restrict_to_window(np.array(t_cubic_8bit), np.array(y_cubic_8bit))
                    t_cubic_12bit, y_cubic_12bit = restrict_to_window(np.array(t_cubic_12bit), np.array(y_cubic_12bit))

                    # Polynomial
                    t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
                    t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
                    t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

                    t_poly_ideal, y_poly_ideal = restrict_to_window(np.array(t_poly_ideal), np.array(y_poly_ideal))
                    t_poly_8bit, y_poly_8bit = restrict_to_window(np.array(t_poly_8bit), np.array(y_poly_8bit))
                    t_poly_12bit, y_poly_12bit = restrict_to_window(np.array(t_poly_12bit), np.array(y_poly_12bit))

                    # Restrict raw samples
                    t_samples_ideal, y_samples_ideal = restrict_to_window(np.array(t_samples_ideal), np.array(y_samples_ideal))
                    t_samples_8bit, y_samples_8bit = restrict_to_window(np.array(t_samples_8bit), np.array(y_samples_8bit))
                    t_samples_12bit, y_samples_12bit = restrict_to_window(np.array(t_samples_12bit), np.array(y_samples_12bit))

                    # Raw samples
                    integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
                    integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
                    integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
                    _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
                    _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
                    _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

                    # Linear interpolation
                    integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
                    integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
                    integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
                    _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
                    _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
                    _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

                    # Cubic spline interpolation
                    integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
                    integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
                    integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
                    _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
                    _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
                    _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

                    # Polynomial interpolation
                    integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
                    integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
                    integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
                    _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
                    _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
                    _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

                    # Update maximum errors
                    for interp, rel_errs in zip(
                        ['raw', 'linear', 'cubic', 'poly'],
                        [
                            [rel_err_ideal, rel_err_8bit, rel_err_12bit],
                            [rel_err_linear_ideal, rel_err_linear_8bit, rel_err_linear_12bit],
                            [rel_err_cubic_ideal, rel_err_cubic_8bit, rel_err_cubic_12bit],
                            [rel_err_poly_ideal, rel_err_poly_8bit, rel_err_poly_12bit]
                        ]
                    ):
                        for adc, rel_err in zip(['n-bit', '8bit', '12bit'], rel_errs):
                            if rel_err > max_errors[interp][adc][sps]['max_error']:
                                max_errors[interp][adc][sps]['max_error'] = rel_err
                                max_errors[interp][adc][sps]['phase'] = phase_deg

                except Exception as e:
                    error_count += 1
                    # print(f"Błąd dla amplitude={amplitude}, phase={phase_deg}, num_samples={num_samples}: {e}")
                    continue

        # Text results
        print(f"\n\n===== AMPLITUDE: {A} V =====")
        for interp_type, interp_label in interp_names.items():
            print(f"\n{interp_label}")
            print("{:^15} | {:^10} | {:^15} | {:^10}".format(
                "samples per sigma", "Typ ADC", "Max błąd wzgl. [%]", "Faza [°]"))
            print("-"*60)
            for sps in samples_per_sigma:
                for adc_type, adc_label in adc_names.items():
                    result = max_errors[interp_type][adc_type][sps]
                    print("{:^12} | {:^15} | {:^15.5f} | {:^10}".format(
                        sps, adc_label, result['max_error'], result['phase']))
                print("-"*60)

        # Plots
        x = samples_per_sigma # [1, 2, 3, 4]
        x_labels = [str(sps) for sps in samples_per_sigma]
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Maksymalne błędy względne dla amplitudy {A} V", fontsize=28)
        n_rows = len(interp_names) - 1
        plot_num = 1
        for interp_type, interp_label in interp_names.items():
            if interp_type != 'raw':
                ax = fig.add_subplot(n_rows, 1, plot_num)
                for adc_type, adc_label in adc_names.items():
                    y_values = [max_errors[interp_type][adc_type][sps]['max_error'] for sps in samples_per_sigma]
                    ax.plot(x, y_values, marker='o', label=adc_label)
                ax.set_ylabel(f"{interp_label}\nBłąd względny [%]", fontsize=12)
                ax.set_xticks(x)
                ax.set_xlim([min(x)-0.2, max(x)+0.2])
                ax.tick_params(axis='x', labelsize=22)
                ax.tick_params(axis='y', labelsize=22)
                if plot_num == n_rows:
                    ax.set_xlabel("samples per sigma", fontsize=28)
                    ax.set_xticklabels(x_labels, fontsize=22)
                else:
                    ax.set_xticklabels([])
                ax.grid(True)
                ax.legend(fontsize=22)
                plot_num += 1
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    plt.show()

    print(f"\nLiczba pominiętych przypadków z błędem: {error_count}")

def error_vs_amplitudes():
    # Test parameters
    tr = 10 * 10**(-9)
    sigma = tr / 1.69
    tau = 3 * sigma
    start_time_orig = -8 * sigma
    stop_time_orig = 6 * tau

    amplitudes = np.arange(0.1, 5.05, 0.1)
    samples_per_sigma = [1, 2, 3, 4]
    phase_step = 1
    phases = range(0, 360, phase_step)
    poly_degree = 20

    # Prepare structure to collect max errors for each amplitude, ADC, SPS, interpolation
    interp_types = ['raw', 'linear', 'cubic', 'poly']
    adc_types = ['n-bit', '8bit', '12bit']
    # max_errors[interp][adc][sps] = [max_error_for_each_amplitude]
    max_errors = {interp: {adc: {sps: [] for sps in samples_per_sigma} for adc in adc_types} for interp in interp_types}

    for A in amplitudes:
        # For each amplitude, collect max error over all phases for each ADC, SPS, interpolation
        local_max = {interp: {adc: {sps: 0 for sps in samples_per_sigma} for adc in adc_types} for interp in interp_types}
        print(f"\nTesting amplitude: {A} V")

        reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)
        print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
        print(f"Oszacowany błąd scipy: {reference_error:.6e}")

        # Loop through different phase shifts (in degrees)
        for phase_deg in phases:
            start_time = start_time_orig + sigma * phase_deg / 360
            stop_time = stop_time_orig + sigma * phase_deg / 360
            # Loop through different sample sizes
            for sps in samples_per_sigma:
                num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
                try:
                    # Raw samples
                    t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
                    t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
                    t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

                    # Interpolations
                    t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
                    t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
                    t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

                    t_linear_ideal, y_linear_ideal = restrict_to_window(np.array(t_linear_ideal), np.array(y_linear_ideal))
                    t_linear_8bit, y_linear_8bit = restrict_to_window(np.array(t_linear_8bit), np.array(y_linear_8bit))
                    t_linear_12bit, y_linear_12bit = restrict_to_window(np.array(t_linear_12bit), np.array(y_linear_12bit))

                    # Cubic
                    t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                    t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                    t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

                    t_cubic_ideal, y_cubic_ideal = restrict_to_window(np.array(t_cubic_ideal), np.array(y_cubic_ideal))
                    t_cubic_8bit, y_cubic_8bit = restrict_to_window(np.array(t_cubic_8bit), np.array(y_cubic_8bit))
                    t_cubic_12bit, y_cubic_12bit = restrict_to_window(np.array(t_cubic_12bit), np.array(y_cubic_12bit))

                    # Polynomial
                    t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
                    t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
                    t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

                    t_poly_ideal, y_poly_ideal = restrict_to_window(np.array(t_poly_ideal), np.array(y_poly_ideal))
                    t_poly_8bit, y_poly_8bit = restrict_to_window(np.array(t_poly_8bit), np.array(y_poly_8bit))
                    t_poly_12bit, y_poly_12bit = restrict_to_window(np.array(t_poly_12bit), np.array(y_poly_12bit))

                    t_samples_ideal, y_samples_ideal = restrict_to_window(np.array(t_samples_ideal), np.array(y_samples_ideal))
                    t_samples_8bit, y_samples_8bit = restrict_to_window(np.array(t_samples_8bit), np.array(y_samples_8bit))
                    t_samples_12bit, y_samples_12bit = restrict_to_window(np.array(t_samples_12bit), np.array(y_samples_12bit))


                    # Raw samples
                    integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
                    integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
                    integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
                    _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
                    _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
                    _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

                    # Linear interpolation
                    integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
                    integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
                    integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
                    _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
                    _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
                    _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

                    # Cubic spline interpolation
                    integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
                    integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
                    integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
                    _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
                    _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
                    _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

                    # Polynomial interpolation
                    integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
                    integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
                    integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
                    _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
                    _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
                    _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

                    # Update local max errors
                    local_max['raw']['n-bit'][sps] = max(local_max['raw']['n-bit'][sps], abs(rel_err_ideal))
                    local_max['raw']['8bit'][sps] = max(local_max['raw']['8bit'][sps], abs(rel_err_8bit))
                    local_max['raw']['12bit'][sps] = max(local_max['raw']['12bit'][sps], abs(rel_err_12bit))

                    local_max['linear']['n-bit'][sps] = max(local_max['linear']['n-bit'][sps], abs(rel_err_linear_ideal))
                    local_max['linear']['8bit'][sps] = max(local_max['linear']['8bit'][sps], abs(rel_err_linear_8bit))
                    local_max['linear']['12bit'][sps] = max(local_max['linear']['12bit'][sps], abs(rel_err_linear_12bit))

                    local_max['cubic']['n-bit'][sps] = max(local_max['cubic']['n-bit'][sps], abs(rel_err_cubic_ideal))
                    local_max['cubic']['8bit'][sps] = max(local_max['cubic']['8bit'][sps], abs(rel_err_cubic_8bit))
                    local_max['cubic']['12bit'][sps] = max(local_max['cubic']['12bit'][sps], abs(rel_err_cubic_12bit))

                    local_max['poly']['n-bit'][sps] = max(local_max['poly']['n-bit'][sps], abs(rel_err_poly_ideal))
                    local_max['poly']['8bit'][sps] = max(local_max['poly']['8bit'][sps], abs(rel_err_poly_8bit))
                    local_max['poly']['12bit'][sps] = max(local_max['poly']['12bit'][sps], abs(rel_err_poly_12bit))
                except Exception:
                    continue

        # Save max errors for this amplitude
        for interp in interp_types:
            for adc in adc_types:
                for sps in samples_per_sigma:
                        max_errors[interp][adc][sps].append(local_max[interp][adc][sps])

    # Plotting: for each ADC and each SPS, plot error vs amplitude
    interp_labels = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline',
        'poly': f'Interpolacja wielomianowa {poly_degree} st.'
    }
    adc_labels = {
        'n-bit': 'ADC ∞-bit',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }
    fig_num = 1
    for interp in interp_types:
        for adc in adc_types:
            plt.figure(fig_num)
            for sps in samples_per_sigma:
                y = max_errors[interp][adc][sps]
                label = f"{adc_labels[adc]}, {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę"
                plt.plot(amplitudes, y, marker='o', label=label)
            plt.xlabel("Amplituda [V]", fontsize=28)
            plt.ylabel("Maksymalny błąd względny [%]", fontsize=28)
            plt.title(f"{interp_labels[interp]}: Maksymalny błąd względny vs amplituda dla {adc_labels[adc]}", fontsize=22)
            plt.legend(fontsize=22)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)     
            plt.grid(True)
            plt.tight_layout()
            plt.subplots_adjust(left=0.08, right=0.96)
            fig_num += 1

        for sps in samples_per_sigma:
            plt.figure(fig_num)
            for adc in adc_types:
                y = max_errors[interp][adc][sps]
                label = f"{adc_labels[adc]}"
                plt.plot(amplitudes, y, marker='o', label=label)
            plt.xlabel("Amplituda [V]", fontsize=28)
            plt.ylabel("Maksymalny błąd względny [%]", fontsize=28)
            plt.title(f"{interp_labels[interp]}: Maksymalny błąd względny vs amplituda dla {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę", fontsize=22)
            plt.legend(fontsize=22)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
            plt.grid(True)
            plt.tight_layout()
            plt.subplots_adjust(left=0.08, right=0.96)
            fig_num += 1
    plt.show()

def error_vs_phase():
    # Constants for PMT pulse
    tr = 10.0 * 10**(-9)
    A = 1.0
    sigma = tr / 1.69
    tau = 3 * sigma
    # Start and stop times for the PMT pulse
    start_time_orig = -8 * sigma
    stop_time_orig = 6 * tau

    reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)
    print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
    print(f"Oszacowany błąd scipy: {reference_error:.6e}")


    # Number of samples - based on samples per sigma
    sample_sizes = []
    samples_per_sigma = [1, 2, 3, 4]
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
        sample_sizes.append(num_samples)

    # Phase step (in degrees)
    phase_step = 1
    phases = range(0, 360, phase_step)
    
    # Dictionary to store errors for all phases
    all_phase_errors = {
        'raw': {
            'n-bit': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'linear': {
            'n-bit': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'cubic': {
            'n-bit': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'poly': {
            'n-bit': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        }
    }

    # Names for plot legends
    interp_names = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline',
        'poly': f'Interpolacja wielomianowa {poly_degree} st.'
    }
    
    adc_names = {
        'n-bit': 'ADC ∞-bit',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    
    # Loop through different phase shifts (in degrees)
    for phase_deg in phases:
        start_time = start_time_orig + sigma * phase_deg / 360
        stop_time = stop_time_orig + sigma * phase_deg / 360
        # Loop through different sample sizes
        for sps in samples_per_sigma:
            num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))

            # Generate samples
            t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
            t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
            t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

            # Generate interpolations
            t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
            t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
            t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

            t_linear_ideal, y_linear_ideal = restrict_to_window(np.array(t_linear_ideal), np.array(y_linear_ideal))
            t_linear_8bit, y_linear_8bit = restrict_to_window(np.array(t_linear_8bit), np.array(y_linear_8bit))
            t_linear_12bit, y_linear_12bit = restrict_to_window(np.array(t_linear_12bit), np.array(y_linear_12bit))

            # Cubic
            t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
            t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
            t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

            t_cubic_ideal, y_cubic_ideal = restrict_to_window(np.array(t_cubic_ideal), np.array(y_cubic_ideal))
            t_cubic_8bit, y_cubic_8bit = restrict_to_window(np.array(t_cubic_8bit), np.array(y_cubic_8bit))
            t_cubic_12bit, y_cubic_12bit = restrict_to_window(np.array(t_cubic_12bit), np.array(y_cubic_12bit))

            # Polynomial
            t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
            t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
            t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

            t_poly_ideal, y_poly_ideal = restrict_to_window(np.array(t_poly_ideal), np.array(y_poly_ideal))
            t_poly_8bit, y_poly_8bit = restrict_to_window(np.array(t_poly_8bit), np.array(y_poly_8bit))
            t_poly_12bit, y_poly_12bit = restrict_to_window(np.array(t_poly_12bit), np.array(y_poly_12bit))

            # Restrict raw samples
            t_samples_ideal, y_samples_ideal = restrict_to_window(np.array(t_samples_ideal), np.array(y_samples_ideal))
            t_samples_8bit, y_samples_8bit = restrict_to_window(np.array(t_samples_8bit), np.array(y_samples_8bit))
            t_samples_12bit, y_samples_12bit = restrict_to_window(np.array(t_samples_12bit), np.array(y_samples_12bit))

            
            # Calculate integrals and errors
            # Raw samples
            integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
            integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
            integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)

            _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
            _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
            _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

            # Linear interpolation
            integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
            integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
            integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)

            _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
            _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
            _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

            # Cubic spline interpolation
            integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
            integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
            integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)

            _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
            _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
            _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

            # Polynomial interpolation
            integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
            integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
            integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)

            _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
            _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
            _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

            # Save errors for all phases
            # Raw samples
            all_phase_errors['raw']['n-bit'][sps].append(rel_err_ideal)
            all_phase_errors['raw']['8bit'][sps].append(rel_err_8bit)
            all_phase_errors['raw']['12bit'][sps].append(rel_err_12bit)

            # Linear interpolation
            all_phase_errors['linear']['n-bit'][sps].append(rel_err_linear_ideal)
            all_phase_errors['linear']['8bit'][sps].append(rel_err_linear_8bit)
            all_phase_errors['linear']['12bit'][sps].append(rel_err_linear_12bit)

            # Cubic spline interpolation
            all_phase_errors['cubic']['n-bit'][sps].append(rel_err_cubic_ideal)
            all_phase_errors['cubic']['8bit'][sps].append(rel_err_cubic_8bit)
            all_phase_errors['cubic']['12bit'][sps].append(rel_err_cubic_12bit)

            # Polynomial interpolation
            all_phase_errors['poly']['n-bit'][sps].append(rel_err_poly_ideal)
            all_phase_errors['poly']['8bit'][sps].append(rel_err_poly_8bit)
            all_phase_errors['poly']['12bit'][sps].append(rel_err_poly_12bit)

    # Create plots
    # 1. Plot: Relative error vs phase for different ADC types for each sample size
    for sps in samples_per_sigma:
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę", fontsize=28)

        # List of axes
        axes = [plt.subplot(4, 1, i+1) for i in range(4)]

        # List of interpolation types
        interp_types = list(interp_names.keys())
        
        # For each interpolation type
        for i, interp_type in enumerate(interp_types):
            ax = axes[i]
            
            # For each ADC type
            for adc_type, adc_label in adc_names.items():
                y_values = all_phase_errors[interp_type][adc_type][sps]
                if adc_type == 'n-bit':
                    # For n-bit ADC, plot with a thicker line
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='red')
                elif adc_type == '12bit':
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='C0')
                else:
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='tab:orange')

            # Add labels and grid
            ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]", fontsize=10)
            ax.grid(True)
            ax.legend(fontsize=16)
            
            # Add x-axis label only for the bottom plot
            if i == len(interp_types) - 1:
                ax.set_xlabel("Faza [°]", fontsize=24)
            ax.tick_params(axis='x', labelsize=16)
            ax.tick_params(axis='y', labelsize=16)  
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    # 2. Plot: Relative error vs phase for different sample sizes for each ADC type
    for adc_type, adc_label in adc_names.items():
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {adc_label}", fontsize=28)

        # List of axes
        axes = [plt.subplot(4, 1, i+1) for i in range(4)]

        # List of interpolation types
        interp_types = list(interp_names.keys())
        
        # For each interpolation type
        for i, interp_type in enumerate(interp_types):
            ax = axes[i]
            
            # For each sample size
            for sps in samples_per_sigma:
                y_values = all_phase_errors[interp_type][adc_type][sps]
                ax.plot(phases, y_values, marker='.', label=f"{sps} {'próbka' if sps == 1 else 'próbki'}")

            # Add labels and grid
            ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]", fontsize=10)
            ax.grid(True)
            ax.legend(fontsize=16)
            
            # Add x-axis label only for the bottom plot
            if i == len(interp_types) - 1:
                ax.set_xlabel("Faza [°]", fontsize=24)
            ax.tick_params(axis='x', labelsize=16)
            ax.tick_params(axis='y', labelsize=16)
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    # Show all plots
    plt.show()

def monte_carlo_average_relative_error(num_iterations=1000):
    amplitudes = [0.1, 1.0, 5.0]
    tr = 10 * 10**(-9)
    sigma = tr / 1.69
    tau = 3 * sigma
    start_time_orig = -8 * sigma
    stop_time_orig = 6 * tau
    # Number of samples per sigma
    samples_per_sigma = [1, 2, 3, 4]
   
    # Prepare to collect errors
    errors = {
        'raw': {'n-bit': [], '8bit': [], '12bit': []},
        'linear': {'n-bit': [], '8bit': [], '12bit': []},
        'cubic': {'n-bit': [], '8bit': [], '12bit': []},
        'poly': {'n-bit': [], '8bit': [], '12bit': []}
    }
    for key in errors:
        for adc in errors[key]:
            errors[key][adc] = {sps: [] for sps in samples_per_sigma}
    rng = np.random.default_rng()

    for i in range(num_iterations):
        A = rng.uniform(0.1, 5)
        phase_deg = rng.uniform(0, 360)
        phase_shift = sigma * phase_deg / 360

        reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)

        for sps in samples_per_sigma:
            num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
            start_time = start_time_orig + phase_shift
            stop_time = stop_time_orig + phase_shift
            
            # Generate samples
            t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
            t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
            t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

            # Generate interpolations
            # Linear
            t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
            t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
            t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

            t_linear_ideal, y_linear_ideal = restrict_to_window(np.array(t_linear_ideal), np.array(y_linear_ideal))
            t_linear_8bit, y_linear_8bit = restrict_to_window(np.array(t_linear_8bit), np.array(y_linear_8bit))
            t_linear_12bit, y_linear_12bit = restrict_to_window(np.array(t_linear_12bit), np.array(y_linear_12bit))

            # Cubic
            t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
            t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
            t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

            t_cubic_ideal, y_cubic_ideal = restrict_to_window(np.array(t_cubic_ideal), np.array(y_cubic_ideal))
            t_cubic_8bit, y_cubic_8bit = restrict_to_window(np.array(t_cubic_8bit), np.array(y_cubic_8bit))
            t_cubic_12bit, y_cubic_12bit = restrict_to_window(np.array(t_cubic_12bit), np.array(y_cubic_12bit))

            # Polynomial
            t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
            t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
            t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

            t_poly_ideal, y_poly_ideal = restrict_to_window(np.array(t_poly_ideal), np.array(y_poly_ideal))
            t_poly_8bit, y_poly_8bit = restrict_to_window(np.array(t_poly_8bit), np.array(y_poly_8bit))
            t_poly_12bit, y_poly_12bit = restrict_to_window(np.array(t_poly_12bit), np.array(y_poly_12bit))

            t_samples_ideal, y_samples_ideal = restrict_to_window(np.array(t_samples_ideal), np.array(y_samples_ideal))
            t_samples_8bit, y_samples_8bit = restrict_to_window(np.array(t_samples_8bit), np.array(y_samples_8bit))
            t_samples_12bit, y_samples_12bit = restrict_to_window(np.array(t_samples_12bit), np.array(y_samples_12bit))

            # Raw
            integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
            integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
            integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
            _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
            _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
            _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

            # Linear
            integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
            integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
            integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
            _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
            _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
            _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

            # Cubic
            integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
            integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
            integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
            _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
            _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
            _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

            # Polynomial
            integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
            integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
            integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
            _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
            _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
            _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

            # Save errors
            errors['raw']['n-bit'][sps].append(rel_err_ideal)
            errors['raw']['8bit'][sps].append(rel_err_8bit)
            errors['raw']['12bit'][sps].append(rel_err_12bit)

            errors['linear']['n-bit'][sps].append(rel_err_linear_ideal)
            errors['linear']['8bit'][sps].append(rel_err_linear_8bit)
            errors['linear']['12bit'][sps].append(rel_err_linear_12bit)

            errors['cubic']['n-bit'][sps].append(rel_err_cubic_ideal)
            errors['cubic']['8bit'][sps].append(rel_err_cubic_8bit)
            errors['cubic']['12bit'][sps].append(rel_err_cubic_12bit)

            errors['poly']['n-bit'][sps].append(rel_err_poly_ideal)
            errors['poly']['8bit'][sps].append(rel_err_poly_8bit)
            errors['poly']['12bit'][sps].append(rel_err_poly_12bit)

    # Print results
    print("\nŚredni błąd względny [%] dla różnych częstotliwości próbkowania (Monte Carlo, N={}):".format(num_iterations))
    print("{:^12} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10}".format("Metoda", "ADC", *samples_per_sigma))
    print("-"*70)
    for method in ['raw', 'linear', 'cubic', 'poly']:
        for adc in ['n-bit', '8bit', '12bit']:
            means = [np.mean(errors[method][adc][sps]) for sps in samples_per_sigma]
            print("{:^12} | {:^10} | {:^10.5f} | {:^10.5f} | {:^10.5f} | {:^10.5f}".format(
                method, adc, *means))
        print("-"*70)

    # --- Prepare data for grouped bar chart ---
    interp_labels = ['Bez interpolacji', 'Interpolacja liniowa', f'Interpolacja wielomianowa {poly_degree} st.', 'Interpolacja cubic spline']
    interp_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    adc_labels = {
        'n-bit': 'ADC ∞-bit',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }
    bar_width = 0.18
    x = np.arange(len(samples_per_sigma))  # [0, 1, 2, 3] for SPS=1,2,3,4

    # Calculate mean relative errors for each ADC, SPS, interpolation
    mean_rel_errors = {adc: [] for adc in adc_labels}
    for adc_key in mean_rel_errors:
        for sps in samples_per_sigma:
            mean_raw = np.mean(errors['raw'][adc_key][sps])
            mean_linear = np.mean(errors['linear'][adc_key][sps])
            mean_poly = np.mean(errors['poly'][adc_key][sps])
            mean_cubic = np.mean(errors['cubic'][adc_key][sps])
            mean_rel_errors[adc_key].append([mean_raw, mean_linear, mean_poly, mean_cubic])

    # --- Plot grouped bar charts for each ADC ---
    for adc_key, adc_label in adc_labels.items():
        plt.figure(figsize=(10, 6))
        for i, (interp_label, color) in enumerate(zip(interp_labels, interp_colors)):
            y = [mean_rel_errors[adc_key][j][i] for j in range(len(samples_per_sigma))]
            plt.bar(x + i*bar_width, y, width=bar_width, color=color, label=interp_label, zorder=2)
        plt.xlabel("Liczba próbek na sigmę", fontsize=28)
        plt.ylabel("Średni błąd względny [%]", fontsize=28)
        plt.title(f"Średni błąd względny (Monte Carlo, N={num_iterations}) dla {adc_label}", fontsize=28)
        plt.xticks(x + 1.5*bar_width, samples_per_sigma, fontsize=22)
        plt.yticks(fontsize=22)
        plt.grid(axis='y', linestyle='-', alpha=0.7, zorder=1)
        plt.legend(fontsize=22)
        plt.tight_layout()
    plt.show()

    for A in amplitudes:
        for i in range(num_iterations):
            phase_deg = rng.uniform(0, 360)
            phase_shift = sigma * phase_deg / 360

            reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, integral_window_start, integral_window_stop)

            for sps in samples_per_sigma:
                num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
                start_time = start_time_orig + phase_shift
                stop_time = stop_time_orig + phase_shift
                
                # Generate samples
                t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
                t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
                t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

                # Generate interpolations
                # Linear
                t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
                t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
                t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

                t_linear_ideal, y_linear_ideal = restrict_to_window(np.array(t_linear_ideal), np.array(y_linear_ideal))
                t_linear_8bit, y_linear_8bit = restrict_to_window(np.array(t_linear_8bit), np.array(y_linear_8bit))
                t_linear_12bit, y_linear_12bit = restrict_to_window(np.array(t_linear_12bit), np.array(y_linear_12bit))

                # Cubic
                t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

                t_cubic_ideal, y_cubic_ideal = restrict_to_window(np.array(t_cubic_ideal), np.array(y_cubic_ideal))
                t_cubic_8bit, y_cubic_8bit = restrict_to_window(np.array(t_cubic_8bit), np.array(y_cubic_8bit))
                t_cubic_12bit, y_cubic_12bit = restrict_to_window(np.array(t_cubic_12bit), np.array(y_cubic_12bit))

                # Polynomial
                t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
                t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
                t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

                t_poly_ideal, y_poly_ideal = restrict_to_window(np.array(t_poly_ideal), np.array(y_poly_ideal))
                t_poly_8bit, y_poly_8bit = restrict_to_window(np.array(t_poly_8bit), np.array(y_poly_8bit))
                t_poly_12bit, y_poly_12bit = restrict_to_window(np.array(t_poly_12bit), np.array(y_poly_12bit))

                t_samples_ideal, y_samples_ideal = restrict_to_window(np.array(t_samples_ideal), np.array(y_samples_ideal))
                t_samples_8bit, y_samples_8bit = restrict_to_window(np.array(t_samples_8bit), np.array(y_samples_8bit))
                t_samples_12bit, y_samples_12bit = restrict_to_window(np.array(t_samples_12bit), np.array(y_samples_12bit))

                # Raw
                integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
                integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
                integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
                _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
                _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
                _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

                # Linear
                integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
                integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
                integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
                _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
                _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
                _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

                # Cubic
                integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
                integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
                integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
                _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
                _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
                _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

                # Polynomial
                integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
                integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
                integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
                _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
                _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
                _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

                # Save errors
                errors['raw']['n-bit'][sps].append(rel_err_ideal)
                errors['raw']['8bit'][sps].append(rel_err_8bit)
                errors['raw']['12bit'][sps].append(rel_err_12bit)

                errors['linear']['n-bit'][sps].append(rel_err_linear_ideal)
                errors['linear']['8bit'][sps].append(rel_err_linear_8bit)
                errors['linear']['12bit'][sps].append(rel_err_linear_12bit)

                errors['cubic']['n-bit'][sps].append(rel_err_cubic_ideal)
                errors['cubic']['8bit'][sps].append(rel_err_cubic_8bit)
                errors['cubic']['12bit'][sps].append(rel_err_cubic_12bit)

                errors['poly']['n-bit'][sps].append(rel_err_poly_ideal)
                errors['poly']['8bit'][sps].append(rel_err_poly_8bit)
                errors['poly']['12bit'][sps].append(rel_err_poly_12bit)

        # Print results
        print("\nŚredni błąd względny [%] dla różnych częstotliwości próbkowania (Monte Carlo, N={}, A={}V):".format(num_iterations, A))
        print("{:^12} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10}".format("Metoda", "ADC", *samples_per_sigma))
        print("-"*70)
        for method in ['raw', 'linear', 'cubic', 'poly']:
            for adc in ['n-bit', '8bit', '12bit']:
                means = [np.mean(errors[method][adc][sps]) for sps in samples_per_sigma]
                print("{:^12} | {:^10} | {:^10.5f} | {:^10.5f} | {:^10.5f} | {:^10.5f}".format(
                    method, adc, *means))
            print("-"*70)

def search_amplitude(tr = 20.0 * 10**(-9), A = 1.0):
    print(f"Amplitude: {A:.3e} V")
    sigma = tr / 1.69 # related to rise time
    tau = 3 * sigma # related to fall time

    start_time = -0.8 * tr
    stop_time = -0.2 * tr
    time_step = (stop_time - start_time) * 0.9
    time_arr, y_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)
    print("\nADC 8-bit parameters:")
    time_arr_8bit, y_arr_8bit = sg.sample_signal_ADC_n_bit_ver_2(time_arr, y_arr, 8)
    print("time_arr_8bit:", time_arr_8bit)
    print("y_arr_8bit:", y_arr_8bit)
    print("\nADC 12-bit parameters:")
    time_arr_12bit, y_arr_12bit = sg.sample_signal_ADC_n_bit_ver_2(time_arr, y_arr, 12)
    print("time_arr_12bit:", time_arr_12bit)
    print("y_arr_12bit:", y_arr_12bit)

    print("\nADC ∞-bit results:")
    # Search for time (u) when pulse reaches amplitude (A)
    t = (time_arr[1] - time_arr[0])
    print(f"Time differance (t1-t0): {t:.3e} s")
    tmp = 2 * sigma**2 * np.log(y_arr[1]/y_arr[0])
    print(f"Temporary value (tmp): {tmp:.3e} s^2")
    u  = (t**2 + tmp) / (2 * t)
    A = y_arr[0] * np.exp(0.5 * (u / sigma)**2)
    print(f"Amplitude at time {u:.3e} is {A:.3e} V")

    time_step = u * 2
    time_arr, y_arr = sg.PMT_pulse_values(time_arr[0]+u, time_arr[0]+u*1.1, time_step, A, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)

    print("\nADC 8-bit results:")
    # Search for time (u) when pulse reaches amplitude (A) for ADC 8-bit
    t = (time_arr_8bit[1] - time_arr_8bit[0])
    print(f"Time differance (t1-t0): {t:.3e} s")
    tmp = 2 * sigma**2 * np.log(y_arr_8bit[1]/y_arr_8bit[0])
    print(f"Temporary value (tmp): {tmp:.3e} s^2")
    u  = (t**2 + tmp) / (2 * t)
    A = y_arr_8bit[0] * np.exp(0.5 * (u / sigma)**2)
    print(f"Amplitude at time {u:.3e} is {A:.3e} V")

    time_step = u * 2
    time_arr, y_arr = sg.PMT_pulse_values(time_arr_8bit[0]+u, time_arr_8bit[0]+u*1.1, time_step, A, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)

    print("\nADC 12-bit results:")
    # Search for time (u) when pulse reaches amplitude (A) for ADC 12-bit
    t = (time_arr_12bit[1] - time_arr_12bit[0])
    print(f"Time differance (t1-t0): {t:.3e} s")
    tmp = 2 * sigma**2 * np.log(y_arr_12bit[1]/y_arr_12bit[0])
    print(f"Temporary value (tmp): {tmp:.3e} s^2")
    u  = (t**2 + tmp) / (2 * t)
    A = y_arr_12bit[0] * np.exp(0.5 * (u / sigma)**2)
    print(f"Amplitude at time {u:.3e} is {A:.3e} V")

    time_step = u * 2
    time_arr, y_arr = sg.PMT_pulse_values(time_arr_12bit[0]+u, time_arr_12bit[0]+u*1.1, time_step, A, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)