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

def plot_for_sample_pulse():
    # Constants for PMT pulse
    A = 0.6
    tr = 3.0 * 10**(-9) # pulse rise time
    sigma = tr / 1.69 # related to rise time
    tau = 3 * sigma # related to fall time

    start_time = -5 * sigma
    stop_time = 7 * tau
    time_step = 0.01 * 10**(-9)
    
    start_time = start_time + sigma * 325/360  # Center the pulse around zero
    stop_time = stop_time + sigma * 325/360  # Center the pulse around zero
    # Samples for PMT pulse
    time_arr, value_arr = sg.PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)
    
    # Number of samples - based on samples per sigma
    samples_per_sigma = [1, 2, 3, 4]
    sample_sizes = []
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time - start_time) / sigma))
        sample_sizes.append(num_samples)

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
                f"{num_samples} próbek",
                fig_num,
                "Interpolacja cubic spline"
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
            
            # Calculate integral            integral_val = integral.integrate_rectangle_method(t_interp, y_interp)
            abs_err, rel_err = integral.calculate_error(integral_val, reference_result)
            
            # Print results
            print("{:^10} | {:^20} | {:.4e} | {:.4e} | {:^15.2f}".format(
                num_samples, sample_label, integral_val, abs_err, rel_err))
        
        print("-"*85)
    plt.show()

def worst_case_for_amplitudes():
    # Constants for PMT pulse
    A = [0.05, 0.1, 0.2, 0.5, 1.0]
    tr = 3.0 * 10**(-9)
    sigma = tr / 1.69
    tau = 3 * sigma
    start_time_orig = -5 * sigma
    stop_time_orig = 7 * tau

    # Number of samples - based on samples per sigma
    samples_per_sigma = [1, 2, 3, 4]
    sample_sizes = []
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
        sample_sizes.append(num_samples)

    # Słownik do przechowywania maksymalnych błędów dla różnych amplitud i faz
    max_errors = {}
    
    # Nowy słownik do przechowywania wszystkich błędów dla wszystkich faz
    all_phase_errors = {}
    
    # Krok fazowy (w stopniach)
    phase_step = 5
    phases = range(0, 360, phase_step)
    
    # Inicjalizacja struktury słownika dla każdej amplitudy
    for amplitude in A:
        max_errors[amplitude] = {
            'raw': {
                'ideal': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '8bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '12bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes}
            },
            'linear': {
                'ideal': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '8bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '12bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes}
            },
            'cubic': {
                'ideal': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '8bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes},
                '12bit': {size: {'max_error': 0, 'phase': 0} for size in sample_sizes}
            }
        }
        
        # Inicjalizacja słownika dla wszystkich błędów vs. faza
        all_phase_errors[amplitude] = {
            'raw': {
                'ideal': {size: [] for size in sample_sizes},
                '8bit': {size: [] for size in sample_sizes},
                '12bit': {size: [] for size in sample_sizes}
            },
            'linear': {
                'ideal': {size: [] for size in sample_sizes},
                '8bit': {size: [] for size in sample_sizes},
                '12bit': {size: [] for size in sample_sizes}
            },
            'cubic': {
                'ideal': {size: [] for size in sample_sizes},
                '8bit': {size: [] for size in sample_sizes},
                '12bit': {size: [] for size in sample_sizes}
            }
        }

    # Pętla przez wszystkie amplitudy
    for amplitude in A:
        print(f"\nTesting amplitude: {amplitude}")
        
        # Pętla przez różne przesunięcia fazowe (w stopniach)
        for phase_deg in phases:
            # Zastosuj przesunięcie fazowe do czasów próbkowania
            start_time = start_time_orig + sigma * phase_deg / 360
            stop_time = stop_time_orig + sigma * phase_deg / 360
            
            # Pętla przez różne rozmiary próbek
            for num_samples in sample_sizes:
                # Generowanie próbek
                t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, amplitude, sigma, tau)
                t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, amplitude, sigma, tau, 8)
                t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, amplitude, sigma, tau, 12)
                
                # Generowanie interpolacji
                t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal[1:-2], y_samples_ideal[1:-2])
                t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit[1:-2], y_samples_8bit[1:-2])
                t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit[1:-2], y_samples_12bit[1:-2])
                
                t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
                t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
                t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)
                
                # Zdefiniuj zakres całkowania dla wszystkich metod aby dopasować zakres interpolacji cubic spline
                # Oblicz referencyjną całkę dla tego konkretnego zakresu czasu (dopasowanego do zakresu cubic spline)
                # Funkcja interpolacji cubic spline w pliku interpolation.py używa zakresu t_samples[1] do t_samples[-2]
                reference_start = t_samples_ideal[1]  # Pomiń pierwszą próbkę
                reference_stop = t_samples_ideal[-2]  # Pomiń ostatnią próbkę
                reference_result, reference_error = sg.integrate_PMT_pulse(amplitude, sigma, tau, reference_start, reference_stop)
                
                # Oblicz całki i błędy
                # Surowe próbki - pomiń pierwszą i ostatnią próbkę
                integral_ideal = integral.integrate_rectangle_method(t_samples_ideal[1:-2], y_samples_ideal[1:-2])
                integral_8bit = integral.integrate_rectangle_method(t_samples_8bit[1:-2], y_samples_8bit[1:-2])
                integral_12bit = integral.integrate_rectangle_method(t_samples_12bit[1:-2], y_samples_12bit[1:-2])
                
                _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
                _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
                _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)
                
                # Interpolacja liniowa - zapewniamy, że używamy punktów w tym samym zakresie co cubic spline
                integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
                integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
                integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
                
                _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
                _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
                _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)
                
                # Interpolacja cubic spline - już używa odpowiedniego zakresu w funkcji interpolacji
                integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
                integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
                integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
                
                _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
                _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
                _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)
                
                # Zapisz błędy dla wszystkich faz
                # Surowe próbki
                all_phase_errors[amplitude]['raw']['ideal'][num_samples].append(rel_err_ideal)
                all_phase_errors[amplitude]['raw']['8bit'][num_samples].append(rel_err_8bit)
                all_phase_errors[amplitude]['raw']['12bit'][num_samples].append(rel_err_12bit)
                
                # Interpolacja liniowa
                all_phase_errors[amplitude]['linear']['ideal'][num_samples].append(rel_err_linear_ideal)
                all_phase_errors[amplitude]['linear']['8bit'][num_samples].append(rel_err_linear_8bit)
                all_phase_errors[amplitude]['linear']['12bit'][num_samples].append(rel_err_linear_12bit)
                
                # Interpolacja cubic spline
                all_phase_errors[amplitude]['cubic']['ideal'][num_samples].append(rel_err_cubic_ideal)
                all_phase_errors[amplitude]['cubic']['8bit'][num_samples].append(rel_err_cubic_8bit)
                all_phase_errors[amplitude]['cubic']['12bit'][num_samples].append(rel_err_cubic_12bit)
                
                # Aktualizuj maksymalne błędy dla bieżącej amplitudy
                # Surowe próbki
                if rel_err_ideal > max_errors[amplitude]['raw']['ideal'][num_samples]['max_error']:
                    max_errors[amplitude]['raw']['ideal'][num_samples]['max_error'] = rel_err_ideal
                    max_errors[amplitude]['raw']['ideal'][num_samples]['phase'] = phase_deg
                
                if rel_err_8bit > max_errors[amplitude]['raw']['8bit'][num_samples]['max_error']:
                    max_errors[amplitude]['raw']['8bit'][num_samples]['max_error'] = rel_err_8bit
                    max_errors[amplitude]['raw']['8bit'][num_samples]['phase'] = phase_deg
                
                if rel_err_12bit > max_errors[amplitude]['raw']['12bit'][num_samples]['max_error']:
                    max_errors[amplitude]['raw']['12bit'][num_samples]['max_error'] = rel_err_12bit
                    max_errors[amplitude]['raw']['12bit'][num_samples]['phase'] = phase_deg
                
                # Interpolacja liniowa
                if rel_err_linear_ideal > max_errors[amplitude]['linear']['ideal'][num_samples]['max_error']:
                    max_errors[amplitude]['linear']['ideal'][num_samples]['max_error'] = rel_err_linear_ideal
                    max_errors[amplitude]['linear']['ideal'][num_samples]['phase'] = phase_deg
                
                if rel_err_linear_8bit > max_errors[amplitude]['linear']['8bit'][num_samples]['max_error']:
                    max_errors[amplitude]['linear']['8bit'][num_samples]['max_error'] = rel_err_linear_8bit
                    max_errors[amplitude]['linear']['8bit'][num_samples]['phase'] = phase_deg
                
                if rel_err_linear_12bit > max_errors[amplitude]['linear']['12bit'][num_samples]['max_error']:
                    max_errors[amplitude]['linear']['12bit'][num_samples]['max_error'] = rel_err_linear_12bit
                    max_errors[amplitude]['linear']['12bit'][num_samples]['phase'] = phase_deg
                
                # Interpolacja cubic spline
                if rel_err_cubic_ideal > max_errors[amplitude]['cubic']['ideal'][num_samples]['max_error']:
                    max_errors[amplitude]['cubic']['ideal'][num_samples]['max_error'] = rel_err_cubic_ideal
                    max_errors[amplitude]['cubic']['ideal'][num_samples]['phase'] = phase_deg
                
                if rel_err_cubic_8bit > max_errors[amplitude]['cubic']['8bit'][num_samples]['max_error']:
                    max_errors[amplitude]['cubic']['8bit'][num_samples]['max_error'] = rel_err_cubic_8bit
                    max_errors[amplitude]['cubic']['8bit'][num_samples]['phase'] = phase_deg
                
                if rel_err_cubic_12bit > max_errors[amplitude]['cubic']['12bit'][num_samples]['max_error']:
                    max_errors[amplitude]['cubic']['12bit'][num_samples]['max_error'] = rel_err_cubic_12bit
                    max_errors[amplitude]['cubic']['12bit'][num_samples]['phase'] = phase_deg

    # Nazwy dla legendy wykresów
    interp_names = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline'
    }
    
    adc_names = {
        'ideal': 'Idealny ADC',
        '8bit': 'ADC 8-bit',
        '12bit': 'ADC 12-bit'
    }
    
    print("\n\n===== WYNIKI NAJGORSZYCH PRZYPADKÓW =====")
    
    # Dla każdej amplitudy
    for amplitude in A:
        print(f"\n\n===== AMPLITUDA: {amplitude} V =====")
        
        # Dla każdego typu interpolacji
        for interp_type, interp_label in interp_names.items():
            print(f"\n{interp_label}")
            print("{:^12} | {:^15} | {:^15} | {:^10}".format(
                "Liczba próbek", "Typ ADC", "Max błąd wzgl. [%]", "Faza [°]"))
            print("-"*60)
            
            # Dla każdego rozmiaru próbki
            for num_samples in sample_sizes:
                # Dla każdego typu ADC
                for adc_type, adc_label in adc_names.items():
                    result = max_errors[amplitude][interp_type][adc_type][num_samples]
                    print("{:^12} | {:^15} | {:^15.2f} | {:^10}".format(
                        num_samples, adc_label, result['max_error'], result['phase']))
                print("-"*60)
    
    # 1. Wykresy maksymalnych błędów względnych dla różnych amplitud
    # Rozmiary próbek dla osi x
    x = range(len(sample_sizes))
    x_labels = [str(size) for size in sample_sizes]
    
    # Dla każdej amplitudy, utwórz nowy rysunek
    for amplitude in A:
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Maksymalne błędy względne dla amplitudy {amplitude} V", fontsize=16)
        
        # Zdefiniuj układ siatki w ramach tego rysunku
        n_rows = len(interp_names)
        n_cols = 1  # Jedna kolumna na rysunek
        
        # Licznik wykresów
        plot_num = 1
        
        # Wykres dla każdego typu interpolacji
        for interp_type, interp_label in interp_names.items():
            ax = fig.add_subplot(n_rows, 1, plot_num)
            
            # Wykres dla każdego typu ADC
            for adc_type, adc_label in adc_names.items():
                y_values = [max_errors[amplitude][interp_type][adc_type][size]['max_error'] for size in sample_sizes]
                ax.plot(x, y_values, marker='o', label=adc_label)
            
            # Dodaj etykiety i siatkę
            ax.set_ylabel(f"{interp_label}\nBłąd względny [%]")
            
            if plot_num == n_rows:  # Dolny wiersz
                ax.set_xlabel("Liczba próbek")
                ax.set_xticks(x)
                ax.set_xticklabels(x_labels)
            else:
                ax.set_xticks(x)
                ax.set_xticklabels([])
            
            ax.grid(True)
            ax.legend()
            
            plot_num += 1
        
        # Dostosuj układ
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
    
    # 2. NOWE WYKRESY: Zależność błędu względnego od fazy
    # Dla każdej amplitudy:
    for amplitude in A:
        # Dla każdego rozmiaru próbki:
        for num_samples in sample_sizes:
            fig = plt.figure(figsize=(15, 10))
            fig.suptitle(f"Błąd względny vs. faza dla amplitudy {amplitude} V i {num_samples} próbek", fontsize=16)
            
            # Zdefiniuj układ siatki
            ax1 = plt.subplot(3, 1, 1)  # Bez interpolacji
            ax2 = plt.subplot(3, 1, 2)  # Interpolacja liniowa
            ax3 = plt.subplot(3, 1, 3)  # Interpolacja cubic spline
            
            # Lista osi
            axes = [ax1, ax2, ax3]
            
            # Lista typów interpolacji
            interp_types = list(interp_names.keys())
            
            # Dla każdego typu interpolacji
            for i, interp_type in enumerate(interp_types):
                ax = axes[i]
                
                # Dla każdego typu ADC
                for adc_type, adc_label in adc_names.items():
                    y_values = all_phase_errors[amplitude][interp_type][adc_type][num_samples]
                    ax.plot(phases, y_values, marker='.', label=adc_label)
                
                # Dodaj etykiety i siatkę
                ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]")
                ax.grid(True)
                ax.legend()
                
                # Dodaj etykietę osi x tylko dla dolnego wykresu
                if i == len(interp_types) - 1:
                    ax.set_xlabel("Faza [°]")
            
            # Dostosuj układ
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
    
    # 3. NOWE WYKRESY: Zależność błędu względnego od fazy dla różnych typów ADC
    # Dla każdej amplitudy:
    for amplitude in A:
        # Dla każdego typu ADC:
        for adc_type, adc_label in adc_names.items():
            fig = plt.figure(figsize=(15, 10))
            fig.suptitle(f"Błąd względny vs. faza dla amplitudy {amplitude} V i {adc_label}", fontsize=16)
            
            # Zdefiniuj układ siatki
            ax1 = plt.subplot(3, 1, 1)  # Bez interpolacji
            ax2 = plt.subplot(3, 1, 2)  # Interpolacja liniowa
            ax3 = plt.subplot(3, 1, 3)  # Interpolacja cubic spline
            
            # Lista osi
            axes = [ax1, ax2, ax3]
            
            # Lista typów interpolacji
            interp_types = list(interp_names.keys())
            
            # Dla każdego typu interpolacji
            for i, interp_type in enumerate(interp_types):
                ax = axes[i]
                
                # Dla każdego rozmiaru próbki
                for num_samples in sample_sizes:
                    y_values = all_phase_errors[amplitude][interp_type][adc_type][num_samples]
                    ax.plot(phases, y_values, marker='.', label=f"{num_samples} próbek")
                
                # Dodaj etykiety i siatkę
                ax.set_ylabel(f"{interp_names[interp_type]}\nBłąd względny [%]")
                ax.grid(True)
                ax.legend()
                
                # Dodaj etykietę osi x tylko dla dolnego wykresu
                if i == len(interp_types) - 1:
                    ax.set_xlabel("Faza [°]")
            
            # Dostosuj układ
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
    
    # Pokaż wszystkie wykresy
    plt.show()

def error_vs_phase(A=0.6):
    # Constants for PMT pulse
    tr = 3.0 * 10**(-9)
    sigma = tr / 1.69
    tau = 3 * sigma
    start_time_orig = -5 * sigma
    stop_time_orig = 7 * tau

    # Number of samples - based on samples per sigma
    samples_per_sigma = [1, 2, 3, 4]
    sample_sizes = []
    for sps in samples_per_sigma:
        num_samples = int(sps * ((stop_time_orig - start_time_orig) / sigma))
        sample_sizes.append(num_samples)

    # Phase step (in degrees)
    phase_step = 3
    phases = range(0, 360, phase_step)
    
    # Dictionary to store errors for all phases
    all_phase_errors = {
        'raw': {
            'ideal': {size: [] for size in sample_sizes},
            '8bit': {size: [] for size in sample_sizes},
            '12bit': {size: [] for size in sample_sizes}
        },
        'linear': {
            'ideal': {size: [] for size in sample_sizes},
            '8bit': {size: [] for size in sample_sizes},
            '12bit': {size: [] for size in sample_sizes}
        },
        'cubic': {
            'ideal': {size: [] for size in sample_sizes},
            '8bit': {size: [] for size in sample_sizes},
            '12bit': {size: [] for size in sample_sizes}
        }
    }

    # Names for plot legends
    interp_names = {
        'raw': 'Bez interpolacji',
        'linear': 'Interpolacja liniowa',
        'cubic': 'Interpolacja cubic spline'
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
        for num_samples in sample_sizes:
            # Generate samples
            t_samples_ideal, y_samples_ideal = sg.sample_signal(start_time, stop_time, num_samples, A, sigma, tau)
            t_samples_8bit, y_samples_8bit = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, 8)
            t_samples_12bit, y_samples_12bit = sg.sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, 12)
            
            # Generate interpolations
            t_linear_ideal, y_linear_ideal = interpolation.linear_interpolation(t_samples_ideal[1:-2], y_samples_ideal[1:-2])
            t_linear_8bit, y_linear_8bit = interpolation.linear_interpolation(t_samples_8bit[1:-2], y_samples_8bit[1:-2])
            t_linear_12bit, y_linear_12bit = interpolation.linear_interpolation(t_samples_12bit[1:-2], y_samples_12bit[1:-2])
            
            t_cubic_ideal, y_cubic_ideal = interpolation.cubic_spline_interpolation(t_samples_ideal, y_samples_ideal)
            t_cubic_8bit, y_cubic_8bit = interpolation.cubic_spline_interpolation(t_samples_8bit, y_samples_8bit)
            t_cubic_12bit, y_cubic_12bit = interpolation.cubic_spline_interpolation(t_samples_12bit, y_samples_12bit)
            
            # Define integration range for all methods to match cubic spline interpolation range
            # Calculate reference integral for this specific time range (matched to cubic spline range)
            # The cubic_spline_interpolation function in interpolation.py uses the range t_samples[1] to t_samples[-2]
            reference_start = t_samples_ideal[1]  # Skip first sample
            reference_stop = t_samples_ideal[-2]  # Skip last sample
            reference_result, reference_error = sg.integrate_PMT_pulse(A, sigma, tau, reference_start, reference_stop)
            
            # Calculate integrals and errors
            # Raw samples - skip first and last sample
            integral_ideal = integral.integrate_rectangle_method(t_samples_ideal[1:-2], y_samples_ideal[1:-2])
            integral_8bit = integral.integrate_rectangle_method(t_samples_8bit[1:-2], y_samples_8bit[1:-2])
            integral_12bit = integral.integrate_rectangle_method(t_samples_12bit[1:-2], y_samples_12bit[1:-2])
            
            _, rel_err_ideal = integral.calculate_error(integral_ideal, reference_result)
            _, rel_err_8bit = integral.calculate_error(integral_8bit, reference_result)
            _, rel_err_12bit = integral.calculate_error(integral_12bit, reference_result)
            
            # Linear interpolation - ensure we use points in the same range as cubic spline
            integral_linear_ideal = integral.integrate_rectangle_method(t_linear_ideal, y_linear_ideal)
            integral_linear_8bit = integral.integrate_rectangle_method(t_linear_8bit, y_linear_8bit)
            integral_linear_12bit = integral.integrate_rectangle_method(t_linear_12bit, y_linear_12bit)
            
            _, rel_err_linear_ideal = integral.calculate_error(integral_linear_ideal, reference_result)
            _, rel_err_linear_8bit = integral.calculate_error(integral_linear_8bit, reference_result)
            _, rel_err_linear_12bit = integral.calculate_error(integral_linear_12bit, reference_result)
            
            # Cubic spline interpolation - already uses appropriate range in interpolation function
            integral_cubic_ideal = integral.integrate_rectangle_method(t_cubic_ideal, y_cubic_ideal)
            integral_cubic_8bit = integral.integrate_rectangle_method(t_cubic_8bit, y_cubic_8bit)
            integral_cubic_12bit = integral.integrate_rectangle_method(t_cubic_12bit, y_cubic_12bit)
            
            _, rel_err_cubic_ideal = integral.calculate_error(integral_cubic_ideal, reference_result)
            _, rel_err_cubic_8bit = integral.calculate_error(integral_cubic_8bit, reference_result)
            _, rel_err_cubic_12bit = integral.calculate_error(integral_cubic_12bit, reference_result)
            
            # Save errors for all phases
            # Raw samples
            all_phase_errors['raw']['ideal'][num_samples].append(rel_err_ideal)
            all_phase_errors['raw']['8bit'][num_samples].append(rel_err_8bit)
            all_phase_errors['raw']['12bit'][num_samples].append(rel_err_12bit)
            
            # Linear interpolation
            all_phase_errors['linear']['ideal'][num_samples].append(rel_err_linear_ideal)
            all_phase_errors['linear']['8bit'][num_samples].append(rel_err_linear_8bit)
            all_phase_errors['linear']['12bit'][num_samples].append(rel_err_linear_12bit)
            
            # Cubic spline interpolation
            all_phase_errors['cubic']['ideal'][num_samples].append(rel_err_cubic_ideal)
            all_phase_errors['cubic']['8bit'][num_samples].append(rel_err_cubic_8bit)
            all_phase_errors['cubic']['12bit'][num_samples].append(rel_err_cubic_12bit)
    
    # Create plots
    # 1. Plot: Relative error vs phase for different ADC types for each sample size
    for num_samples in sample_sizes:
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Błąd względny vs. faza dla amplitudy {A} V i {num_samples} próbek", fontsize=16)
        
        # Define grid layout
        ax1 = plt.subplot(3, 1, 1)  # No interpolation
        ax2 = plt.subplot(3, 1, 2)  # Linear interpolation
        ax3 = plt.subplot(3, 1, 3)  # Cubic spline interpolation
        
        # List of axes
        axes = [ax1, ax2, ax3]
        
        # List of interpolation types
        interp_types = list(interp_names.keys())
        
        # For each interpolation type
        for i, interp_type in enumerate(interp_types):
            ax = axes[i]
            
            # For each ADC type
            for adc_type, adc_label in adc_names.items():
                y_values = all_phase_errors[interp_type][adc_type][num_samples]
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
        
        # Define grid layout
        ax1 = plt.subplot(3, 1, 1)  # No interpolation
        ax2 = plt.subplot(3, 1, 2)  # Linear interpolation
        ax3 = plt.subplot(3, 1, 3)  # Cubic spline interpolation
        
        # List of axes
        axes = [ax1, ax2, ax3]
        
        # List of interpolation types
        interp_types = list(interp_names.keys())
        
        # For each interpolation type
        for i, interp_type in enumerate(interp_types):
            ax = axes[i]
            
            # For each sample size
            for num_samples in sample_sizes:
                y_values = all_phase_errors[interp_type][adc_type][num_samples]
                ax.plot(phases, y_values, marker='.', label=f"{num_samples} próbek")
            
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