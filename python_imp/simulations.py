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
    
    start_time = start_time
    stop_time = stop_time
    # Samples for PMT pulse
    time_arr, value_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)
    
    # Number of samples - based on samples per sigma
    sample_sizes = []
    samples_per_sigma = [1, 2, 3]
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time - start_time) / sigma))
        sample_sizes.append(num_samples)

    phase = sigma * 163/360 # phase shift in seconds
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
    for num_samples in sample_sizes:
        # Generate samples
        samples['ideal'][num_samples] = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
        samples['8bit'][num_samples] = sg.sample_signal_ADC_n_bit_ver_2(*samples['ideal'][num_samples], 8)
        samples['12bit'][num_samples] = sg.sample_signal_ADC_n_bit_ver_2(*samples['ideal'][num_samples], 12)
        
        # Generate linear interpolations
        linear_interpolations['ideal'][num_samples] = interpolation.linear_interpolation(*samples['ideal'][num_samples])
        linear_interpolations['8bit'][num_samples] = interpolation.linear_interpolation(*samples['8bit'][num_samples])
        linear_interpolations['12bit'][num_samples] = interpolation.linear_interpolation(*samples['12bit'][num_samples])

        # Generate cubic spline interpolations
        cubic_spline_interpolations['ideal'][num_samples] = interpolation.cubic_spline_interpolation(*samples['ideal'][num_samples])
        cubic_spline_interpolations['8bit'][num_samples] = interpolation.cubic_spline_interpolation(*samples['8bit'][num_samples])
        cubic_spline_interpolations['12bit'][num_samples] = interpolation.cubic_spline_interpolation(*samples['12bit'][num_samples])

        # Generate polynomial (20th degree) interpolations
        polynomial_interpolations['ideal'][num_samples] = interpolation.polynomial_interpolation(samples['ideal'][num_samples][0], samples['ideal'][num_samples][1], poly_degree)
        polynomial_interpolations['8bit'][num_samples] = interpolation.polynomial_interpolation(samples['8bit'][num_samples][0], samples['8bit'][num_samples][1], poly_degree)
        polynomial_interpolations['12bit'][num_samples] = interpolation.polynomial_interpolation(samples['12bit'][num_samples][0], samples['12bit'][num_samples][1], poly_degree)

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
                f"{len(y_samples)} próbek",
                fig_num,
                "Interpolacja liniowa"
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
                f"{len(y_samples)} próbek",
                fig_num,
                "Interpolacja cubic spline"
            )
            fig_num += 1

    # Plot polynomial interpolated signals
    for adc_type in ['ideal', '8bit', '12bit']:
        adc_label = {
            'ideal': 'idealne',
            '8bit': 'ADC 8-bit',
            '12bit': 'ADC 12-bit'
        }[adc_type]

        for num_samples in sample_sizes:
            t_samples, y_samples = samples[adc_type][num_samples]
            t_interp, y_interp = polynomial_interpolations[adc_type][num_samples]

            ps.plot_interpolated_signal(
                f"Interpolacja wielomianowa {poly_degree} st. - {num_samples} próbek ({adc_label})",
                time_arr, value_arr,
                t_samples, y_samples,
                t_interp, y_interp,
                f"{len(y_samples)} próbek",
                fig_num,
                "Interpolacja wielomianowa {poly_degree} st."
            )
            fig_num += 1

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
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
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
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)
    
    for num_samples in sample_sizes:
        for sample_label, sample_key in sampling_types.items():
            # Get interpolated samples
            t_interp, y_interp = cubic_spline_interpolations[sample_key][num_samples]
            
            # Calculate integral 
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)

            #calculate errors
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        
        print("-"*85)
    
    # Integral calculation for polynomial interpolated signals
    print("\nInterpolacja wielomianowa st. {}".format(poly_degree))
    print("\n{:^10} | {:^20} | {:^15} | {:^15} | {:^15}".format("Ilość próbek", "Typ próbkowania", "Całka", "Błąd bezwz.", "Błąd wzg. [%]"))
    print("-"*85)

    for num_samples in sample_sizes:
        for sample_label, sample_key in sampling_types.items():
            t_interp, y_interp = polynomial_interpolations[sample_key][num_samples]
            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        print("-"*85)

    plt.show()

def worst_case_for_amplitudes():
    # Parametry testowe
    tr_list = [1.0e-9, 5.0e-9, 10.0e-9, 25.0e-9, 50.0e-9]
    samples_per_sigma = [1, 2, 3, 4]
    phase_step = 1
    phases = range(0, 360, phase_step)
    poly_degree = 20

    error_count = 0  # Licznik błędów

    # Słowniki do przechowywania wyników
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

    # Główna pętla po różnych czasach narastania
    for trise in tr_list:
        amplitude = trise * 1e8
        sigma = trise / 1.69
        tau = 3 * sigma
        start_time_orig = -8 * sigma
        stop_time_orig = 6 * tau

        # Struktura do przechowywania maksymalnych błędów
        max_errors = {
            interp: {
                adc: {sps: {'max_error': 0, 'phase': 0} for sps in samples_per_sigma}
                for adc in adc_names
            }
            for interp in interp_names
        }

        print(f"\nTesting amplitude: {amplitude} V, rise time: {trise*10**9} ns")

        # Pętla po fazach i rozmiarach próbek
        for phase_deg in phases:
            phase_shift = sigma * phase_deg / 360
            start_time = start_time_orig + phase_shift
            stop_time = stop_time_orig + phase_shift

            for sps in samples_per_sigma:
                num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
                try:
                    # Generowanie próbek
                    t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, amplitude, sigma, tau)
                    t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 8)
                    t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit_ver_2(t_samples_ideal, y_samples_ideal, 12)

                    # Interpolacje
                    t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal, y_samples_ideal)
                    t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit, y_samples_8bit)
                    t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit, y_samples_12bit)

                    t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                    t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                    t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)

                    t_poly_ideal, y_poly_ideal = interpolation.polynomial_interpolation(t_samples_ideal, y_samples_ideal, poly_degree)
                    t_poly_8bit, y_poly_8bit = interpolation.polynomial_interpolation(t_samples_8bit, y_samples_8bit, poly_degree)
                    t_poly_12bit, y_poly_12bit = interpolation.polynomial_interpolation(t_samples_12bit, y_samples_12bit, poly_degree)

                    # Całka referencyjna
                    reference_result, _ = sg.integrate_PMT_pulse(amplitude, sigma, tau, start_time, stop_time)

                    # Surowe próbki
                    integral_ideal = integral.integrate_rectangle_method(t_samples_ideal, y_samples_ideal)
                    integral_8bit = integral.integrate_rectangle_method(t_samples_8bit, y_samples_8bit)
                    integral_12bit = integral.integrate_rectangle_method(t_samples_12bit, y_samples_12bit)
                    _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
                    _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
                    _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)

                    # Interpolacja liniowa
                    integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
                    integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
                    integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
                    _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
                    _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
                    _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)

                    # Interpolacja cubic spline
                    integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
                    integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
                    integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
                    _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
                    _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
                    _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)

                    # Interpolacja wielomianowa
                    integral_poly_ideal = integral.integrate_rectangle_method(t_poly_ideal, y_poly_ideal)
                    integral_poly_8bit = integral.integrate_rectangle_method(t_poly_8bit, y_poly_8bit)
                    integral_poly_12bit = integral.integrate_rectangle_method(t_poly_12bit, y_poly_12bit)
                    _, rel_err_poly_ideal = integral.calculate_error(integral_poly_ideal, reference_result)
                    _, rel_err_poly_8bit = integral.calculate_error(integral_poly_8bit, reference_result)
                    _, rel_err_poly_12bit = integral.calculate_error(integral_poly_12bit, reference_result)

                    # Aktualizacja maksymalnych błędów
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

        # --- Wyniki tekstowe ---
        print(f"\n\n===== AMPLITUDA: {amplitude} V =====")
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

        # --- Wykresy ---
        x = range(len(samples_per_sigma))
        x_labels = [str(sps) for sps in samples_per_sigma]
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Maksymalne błędy względne dla amplitudy {amplitude} V", fontsize=16)
        n_rows = len(interp_names)
        plot_num = 1
        for interp_type, interp_label in interp_names.items():
            ax = fig.add_subplot(n_rows, 1, plot_num)
            for adc_type, adc_label in adc_names.items():
                y_values = [max_errors[interp_type][adc_type][sps]['max_error'] for sps in samples_per_sigma]
                ax.plot(x, y_values, marker='o', label=adc_label)
            ax.set_ylabel(f"{interp_label}\nBłąd względny [%]")
            if plot_num == n_rows:
                ax.set_xlabel("samples per sigma")
                ax.set_xticks(x)
                ax.set_xticklabels(x_labels)
            else:
                ax.set_xticks(x)
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


            #  Oblicz wartość całki referencyjnej dla wszystkich metod
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

            # Poly interpolation
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
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {sps} próbek na sigme", fontsize=16)

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
                ax.plot(phases, y_values, marker='.', label=adc_label)
            
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
                y_values = all_phase_errors[interp_type][adc_type][sps]
                ax.plot(phases, y_values, marker='.', label=f"{sps} próbek")

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

            # Polynomial 3rd degree
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

            # Poly3
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