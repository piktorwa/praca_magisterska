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

def plot_for_sample_pulse():
    # Constants for PMT pulse
    tr = 10.0 * 10**(-9) # pulse rise time
    A = 10**8 * tr # amplitude of the pulse in V
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

    phase = sigma * 347/360 # phase shift in seconds
    start_time += phase
    stop_time += phase

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

    polynomial_interpolations = {
        'ideal': {},
        '8bit': {},
        '12bit': {}
    }
    
    # Generate all samples and interpolations
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time - start_time) / sigma))
        # Generate samples
        samples['ideal'][sps] = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
        samples['8bit'][sps] = sg.sample_signal_ADC_n_bit_ver_2(*samples['ideal'][sps], 8)
        samples['12bit'][sps] = sg.sample_signal_ADC_n_bit_ver_2(*samples['ideal'][sps], 12)

        # Generate linear interpolations
        linear_interpolations['ideal'][sps] = interpolation.linear_interpolation(*samples['ideal'][sps])
        linear_interpolations['8bit'][sps] = interpolation.linear_interpolation(*samples['8bit'][sps])
        linear_interpolations['12bit'][sps] = interpolation.linear_interpolation(*samples['12bit'][sps])

        # Generate cubic spline interpolations
        cubic_spline_interpolations['ideal'][sps] = interpolation.cubic_spline_interpolation(*samples['ideal'][sps])
        cubic_spline_interpolations['8bit'][sps] = interpolation.cubic_spline_interpolation(*samples['8bit'][sps])
        cubic_spline_interpolations['12bit'][sps] = interpolation.cubic_spline_interpolation(*samples['12bit'][sps])

        # Generate polynomial interpolations
        polynomial_interpolations['ideal'][sps] = interpolation.polynomial_interpolation(samples['ideal'][sps][0], samples['ideal'][sps][1], poly_degree)
        polynomial_interpolations['8bit'][sps] = interpolation.polynomial_interpolation(samples['8bit'][sps][0], samples['8bit'][sps][1], poly_degree)
        polynomial_interpolations['12bit'][sps] = interpolation.polynomial_interpolation(samples['12bit'][sps][0], samples['12bit'][sps][1], poly_degree)

    # Plot sampled signals
        
    # --- Plot 1: Only the reference pulse ---
    plt.figure(1)
    plt.plot(np.array(time_arr)*1e9, value_arr, label="puls PMT")
    plt.xlabel("Czas [ns]")
    plt.ylabel("Amplituda [V]")
    plt.title("Referencyjny puls PMT")
    plt.legend()
    plt.grid()

    # --- Plot 2+: Pulse with overlaid samples for each ADC type and sample size ---
    fig_num = 2
    adc_types = ['ideal', '8bit', '12bit']
    adc_labels = {
        'ideal': 'Idealny ADC',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    for adc_type in adc_types:
        for sps in samples_per_sigma:
            t_samples, y_samples = samples[adc_type][sps]
            plt.figure(fig_num)
            plt.plot(np.array(time_arr)*1e9, value_arr, label="PMT pulse")
            plt.plot(np.array(t_samples)*1e9, y_samples, 'ro', linestyle='', label=f"{sps} SPS")
            plt.xlabel("Czas [ns]")
            plt.ylabel("Amplituda [V]")
            plt.title(f"Próbki {adc_labels[adc_type]} - {sps} {'próbka' if sps == 1 else 'próbki'} na sigmę")
            plt.legend()
            plt.grid()
            fig_num += 1
    
    # For ideal sampling
    t_samples_list_ideal = [samples['ideal'][sps][0] for sps in samples_per_sigma]
    y_samples_list_ideal = [samples['ideal'][sps][1] for sps in samples_per_sigma]
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
    t_raw, y_raw = samples['ideal'][sps]

    # Linear interpolation
    t_linear, y_linear = linear_interpolations['ideal'][sps]

    # Cubic spline interpolation
    t_cubic, y_cubic = cubic_spline_interpolations['ideal'][sps]

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
    reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, start_time, stop_time)
    print(f"\nScipy quad całka (referencyjna): {reference_result:.6e}")
    print(f"Oszacowany błąd scipy: {reference_error:.6e}")

    # Table header
    print("\nBez interpolacji")
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    # Integral calculation for sampled signals - Rectangle method
    sampling_types = {
        'Idealny ADC': 'ideal', 
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
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.3f}".format(
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
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.3f}".format(
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
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.3f}".format(
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
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.3f}".format(
                sps, sample_label, integral_val, abs_err, rel_err))
        print("-"*85)

    plt.show()

def worst_case_for_amplitudes():
    # Test parameters
    tr_list = [1.0e-9, 5.0e-9, 10.0e-9, 25.0e-9, 50.0e-9]
    samples_per_sigma = [1, 2, 3, 4]
    phase_step = 1
    phases = range(0, 360, phase_step)
    poly_degree = 20

    error_count = 0  # Error counter

    # Dictionaries to store results
    interp_names = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline',
        'poly': f'Interpolacja wielomianowa {poly_degree} st.'
    }
    adc_names = {
        'ideal': 'Idealny ADC',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    # Main loop over different rise times
    for trise in tr_list:
        amplitude = trise * 1e8
        sigma = trise / 1.69
        tau = 3 * sigma
        start_time_orig = -8 * sigma
        stop_time_orig = 6 * tau

        # Structure to store maximum errors
        max_errors = {
            interp: {
                adc: {sps: {'max_error': 0, 'phase': 0} for sps in samples_per_sigma}
                for adc in adc_names
            }
            for interp in interp_names
        }

        print(f"\nTesting amplitude: {amplitude} V, rise time: {trise*10**9} ns")

        # Loop over phases and sample sizes
        for phase_deg in phases:
            phase_shift = sigma * phase_deg / 360
            start_time = start_time_orig + phase_shift
            stop_time = stop_time_orig + phase_shift

            for sps in samples_per_sigma:
                num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
                try:
                    # Raw samples
                    t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, amplitude, sigma, tau)
                    t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
                    t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

                    # Interpolations
                    # Linear interpolation
                    t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
                    t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
                    t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)
                    # Cubic spline interpolation
                    t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                    t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                    t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)
                    # Polynomial interpolation
                    t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
                    t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
                    t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

                    # Reference integral result
                    reference_result, _ = sg.integrate_PMT_pulse(amplitude, sigma, tau, start_time, stop_time)

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
                        for adc, rel_err in zip(['ideal', '8bit', '12bit'], rel_errs):
                            if rel_err > max_errors[interp][adc][sps]['max_error']:
                                max_errors[interp][adc][sps]['max_error'] = rel_err
                                max_errors[interp][adc][sps]['phase'] = phase_deg

                except Exception as e:
                    error_count += 1
                    # print(f"Błąd dla amplitude={amplitude}, phase={phase_deg}, num_samples={num_samples}: {e}")
                    continue

        # Text results
        print(f"\n\n===== AMPLITUDE: {amplitude} V =====")
        for interp_type, interp_label in interp_names.items():
            print(f"\n{interp_label}")
            print("{:^15} | {:^10} | {:^15} | {:^10}".format(
                "samples per sigma", "Typ ADC", "Max błąd wzgl. [%]", "Faza [°]"))
            print("-"*60)
            for sps in samples_per_sigma:
                for adc_type, adc_label in adc_names.items():
                    result = max_errors[interp_type][adc_type][sps]
                    print("{:^12} | {:^15} | {:^15.2f} | {:^10}".format(
                        sps, adc_label, result['max_error'], result['phase']))
                print("-"*60)

        # Plots
        x = samples_per_sigma # [1, 2, 3, 4]
        x_labels = [str(sps) for sps in samples_per_sigma]
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Maksymalne błędy względne dla amplitudy {amplitude} V", fontsize=16)
        n_rows = len(interp_names)
        plot_num = 1
        for interp_type, interp_label in interp_names.items():
            ax = fig.add_subplot(n_rows, 1, plot_num)
            for adc_type, adc_label in adc_names.items():
                if interp_type == 'poly':
                    y_values = [
                        max_errors[interp_type][adc_type][sps]['max_error'] if sps != 1 else np.nan
                        for sps in samples_per_sigma
                    ]
                    ax.plot(x, y_values, marker='o', label=adc_label)
                else:
                    y_values = [max_errors[interp_type][adc_type][sps]['max_error'] for sps in samples_per_sigma]
                    ax.plot(x, y_values, marker='o', label=adc_label)
            ax.set_ylabel(f"{interp_label}\nBłąd względny [%]")
            ax.set_xticks(x)
            ax.set_xlim([min(x)-0.2, max(x)+0.2])
            if plot_num == n_rows:
                ax.set_xlabel("samples per sigma")
                ax.set_xticklabels(x_labels)
            else:
                ax.set_xticklabels([])
            ax.grid(True)
            ax.legend()
            plot_num += 1
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    plt.show()

    print(f"\nLiczba pominiętych przypadków z błędem: {error_count}")

def error_vs_phase():
    # Constants for PMT pulse
    tr = 10.0 * 10**(-9)
    A = 10**8 * tr
    sigma = tr / 1.69
    tau = 3 * sigma
    # Start and stop times for the PMT pulse
    start_time_orig = -8 * sigma
    stop_time_orig = 6 * tau

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
            'ideal': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'linear': {
            'ideal': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'cubic': {
            'ideal': {sps: [] for sps in samples_per_sigma},
            '8bit': {sps: [] for sps in samples_per_sigma},
            '12bit': {sps: [] for sps in samples_per_sigma}
        },
        'poly': {
            'ideal': {sps: [] for sps in samples_per_sigma},
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
        'ideal': 'Idealny ADC',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }

    # Loop through different phase shifts (in degrees)
    for phase_deg in phases:
        # Apply phase shift to sampling times
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

            t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
            t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
            t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)
            
            t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
            t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
            t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)


            #  Reference integral result
            reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, start_time, stop_time)
            
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
            all_phase_errors['raw']['ideal'][sps].append(rel_err_ideal)
            all_phase_errors['raw']['8bit'][sps].append(rel_err_8bit)
            all_phase_errors['raw']['12bit'][sps].append(rel_err_12bit)

            # Linear interpolation
            all_phase_errors['linear']['ideal'][sps].append(rel_err_linear_ideal)
            all_phase_errors['linear']['8bit'][sps].append(rel_err_linear_8bit)
            all_phase_errors['linear']['12bit'][sps].append(rel_err_linear_12bit)

            # Cubic spline interpolation
            all_phase_errors['cubic']['ideal'][sps].append(rel_err_cubic_ideal)
            all_phase_errors['cubic']['8bit'][sps].append(rel_err_cubic_8bit)
            all_phase_errors['cubic']['12bit'][sps].append(rel_err_cubic_12bit)

            # Polynomial interpolation
            all_phase_errors['poly']['ideal'][sps].append(rel_err_poly_ideal)
            all_phase_errors['poly']['8bit'][sps].append(rel_err_poly_8bit)
            all_phase_errors['poly']['12bit'][sps].append(rel_err_poly_12bit)

    # Create plots
    # 1. Plot: Relative error vs phase for different ADC types for each sample size
    for sps in samples_per_sigma:
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {sps} {'próbka' if sps == 1 else 'próbki'} na sigme", fontsize=16)

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
                if adc_type == 'ideal':
                    # For ideal ADC, plot with a thicker line
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='red')
                elif adc_type == '12bit':
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='C0')
                else:
                    ax.plot(phases, y_values, marker='.', label=adc_label, color='tab:orange')

            # Add labels and grid
            ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]")
            ax.grid(True)
            ax.legend()
            
            # Add x-axis label only for the bottom plot
            if i == len(interp_types) - 1:
                ax.set_xlabel("Faza [°]")
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    # 2. Plot: Relative error vs phase for different sample sizes for each ADC type
    for adc_type, adc_label in adc_names.items():
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {adc_label}", fontsize=16)
        
        # List of axes
        axes = [plt.subplot(4, 1, i+1) for i in range(4)]

        # List of interpolation types
        interp_types = list(interp_names.keys())
        
        # For each interpolation type
        for i, interp_type in enumerate(interp_types):
            ax = axes[i]
            
            # For each sample size
            for sps in samples_per_sigma:
                if interp_type == 'poly' and sps == 1:
                    # Skip polynomial interpolation for 1 sample per sigma
                    continue
                y_values = all_phase_errors[interp_type][adc_type][sps]
                ax.plot(phases, y_values, marker='.', label=f"{sps} {'próbka' if sps == 1 else 'próbki'}")

            # Add labels and grid
            ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]")
            ax.grid(True)
            ax.legend()
            
            # Add x-axis label only for the bottom plot
            if i == len(interp_types) - 1:
                ax.set_xlabel("Faza [°]")
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    # Show all plots
    plt.show()

def monte_carlo_average_relative_error(num_iterations=1000):
    # Number of samples per sigma
    samples_per_sigma = [1, 2, 3, 4]
   
    # Prepare to collect errors
    errors = {
        'raw': {'ideal': [], '8bit': [], '12bit': []},
        'linear': {'ideal': [], '8bit': [], '12bit': []},
        'cubic': {'ideal': [], '8bit': [], '12bit': []},
        'poly': {'ideal': [], '8bit': [], '12bit': []}
    }
    for key in errors:
        for adc in errors[key]:
            errors[key][adc] = {sps: [] for sps in samples_per_sigma}
    rng = np.random.default_rng()

    for i in range(num_iterations):
        tr = rng.uniform(1*10**(-9), 50*10**(-9))
        amplitude = tr * 1e8
        sigma = tr / 1.69
        tau = 3 * sigma
        start_time_orig = -8 * sigma
        stop_time_orig = 6 * tau

        phase_deg = rng.uniform(0, 360)
        phase_shift = sigma * phase_deg / 360

        for sps in samples_per_sigma:
            num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
            start_time = start_time_orig + phase_shift
            stop_time = stop_time_orig + phase_shift
            
            # Generate samples
            t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, amplitude, sigma, tau)
            t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
            t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)
            
            # Generate interpolations
            # Linear
            t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
            t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
            t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

            # Cubic
            t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
            t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
            t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

            # Polynomial
            t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
            t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
            t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

            reference_result, _ = sg.integrate_PMT_pulse(amplitude, sigma, tau, start_time, stop_time)

            # Raw
            integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
            integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
            integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
            _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
            _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
            _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)
            errors['raw']['ideal'][sps].append(rel_err_ideal)
            errors['raw']['8bit'][sps].append(rel_err_8bit)
            errors['raw']['12bit'][sps].append(rel_err_12bit)

            # Linear
            integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
            integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
            integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
            _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
            _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
            _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)
            errors['linear']['ideal'][sps].append(rel_err_linear_ideal)
            errors['linear']['8bit'][sps].append(rel_err_linear_8bit)
            errors['linear']['12bit'][sps].append(rel_err_linear_12bit)

            # Cubic
            integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
            integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
            integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
            _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
            _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
            _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)
            errors['cubic']['ideal'][sps].append(rel_err_cubic_ideal)
            errors['cubic']['8bit'][sps].append(rel_err_cubic_8bit)
            errors['cubic']['12bit'][sps].append(rel_err_cubic_12bit)

            # Polynomial
            integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
            integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
            integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
            _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
            _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
            _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)
            errors['poly']['ideal'][sps].append(rel_err_poly_ideal)
            errors['poly']['8bit'][sps].append(rel_err_poly_8bit)
            errors['poly']['12bit'][sps].append(rel_err_poly_12bit)

    # Print results
    print("\nŚredni błąd względny [%] dla różnych częstotliwości próbkowania (Monte Carlo, N={}):".format(num_iterations))
    print("{:^12} | {:^10} | {:^10} | {:^10} | {:^10} | {:^10}".format("Metoda", "ADC", *samples_per_sigma))
    print("-"*70)
    for method in ['raw', 'linear', 'cubic', 'poly']:
        for adc in ['ideal', '8bit', '12bit']:
            means = [np.mean(errors[method][adc][sps]) for sps in samples_per_sigma]
            print("{:^12} | {:^10} | {:^10.3f} | {:^10.3f} | {:^10.3f} | {:^10.3f}".format(
                method, adc, *means))
        print("-"*70)

def search_amplitude():
    # Constants for PMT pulse
    tr = 20.0 * 10**(-9) # pulse rise time
    amplitude = 10**8 * tr # amplitude of the pulse in V
    print(f"Amplitude: {amplitude:.3e} V")
    sigma = tr / 1.69 # related to rise time
    tau = 3 * sigma # related to fall time

    start_time = -0.8 * tr
    stop_time = -0.2 * tr
    time_step = (stop_time - start_time) * 0.9
    time_arr, y_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, amplitude, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)

    # Search for time (u) when pulse reaches amplitude (A)
    t = (time_arr[1] - time_arr[0])
    print(f"Time differance (t1-t0): {t:.3e} s")
    tmp = 2 * sigma**2 * np.log(y_arr[1]/y_arr[0])
    print(f"Temporary value (tmp): {tmp:.3e} s^2")
    u  = (t**2 + tmp) / (2 * t)
    A = y_arr[0] * np.exp(0.5 * (u / sigma)**2)
    print(f"Amplitude at time {u:.3e} is {A:.3e} V")

    time_step = u * 2
    time_arr, y_arr = sg.PMT_pulse_values(time_arr[0]+u, time_arr[0]+u*1.1, time_step, amplitude, sigma, tau)
    print("time_arr:", time_arr)
    print("y_arr:", y_arr)