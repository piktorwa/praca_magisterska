# Author: Witkor Pantak
# Date: 2025-03-27
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: This is the main file for the project. It will be used to run the project and call the other files.
import matplotlib.pyplot as plt
import numpy as np
import math as m
import scipy.integrate as spi

def exp_PMT_pulse_fun(t, A, sigma, tau):
    C = m.exp(-0.5 * (sigma * tau) * (sigma * tau))  # normalization constant
    th = 2 * sigma * sigma / tau  # threshold time

    if t <= th:
        return A * m.exp(-0.5 * (t / sigma) * (t / sigma))
    else:
        return A / C * m.exp(-1.0 * (t / tau))

def PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau):
    time_arr = np.arange(start_time, stop_time, time_step, dtype=float)
    value_arr = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in time_arr])
    return time_arr, value_arr

def sample_signal(start_time, stop_time, num_samples, A, sigma, tau):
    t_samples = np.linspace(start_time, stop_time, num_samples)
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    return t_samples, y_samples

def sample_signal_ADC_8_bit(start_time, stop_time, num_samples, A, sigma, tau):    
    t_samples = np.linspace(start_time, stop_time, num_samples)
    step = A / 2**8  # 8-bit ADC step size
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    y_samples = np.round(y_samples / step) * step # Quantize to 8-bit levels
    return t_samples, y_samples

def sample_signal_ADC_12_bit(start_time, stop_time, num_samples, A, sigma, tau):
    t_samples = np.linspace(start_time, stop_time, num_samples)
    step = A / 2**12  # 12-bit ADC step size
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples]) 
    y_samples = np.round(y_samples / step) * step # Quantize to 12-bit levels
    return t_samples, y_samples

def plot_sampled_signal(title, time_arr, value_arr, sampling_function, sample_sizes, markers, A, sigma, tau, start_time, stop_time, fig_num):
    plt.figure(fig_num)
    plt.plot(time_arr, value_arr, label="Puls z fotopowielacza")

    for i, num_samples in enumerate(sample_sizes):
        t_samples, y_samples = sampling_function(start_time, stop_time, num_samples, A, sigma, tau)
        plt.plot(t_samples, y_samples, marker=markers[i], linestyle='', label=f'{num_samples} próbek')

    plt.xlabel("Czas (s)")
    plt.ylabel("Amplituda [V]")
    plt.title(title)
    plt.legend()
    plt.grid()

def main():
    A = 0.6
    sigma = 3.0 * 10**(-9)
    tau = 9.0 * 10**(-9)

    start_time = -10 * 10**(-9)
    stop_time = 15 * 10**(-9)
    time_step = 0.001 * 10**(-9)

    time_arr, value_arr = PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau)

    sample_sizes = [8, 16, 32]
    markers = ['o', 's', 'D']

    # Rysowanie dla różnych metod próbkowania
    plot_sampled_signal("Próbkowanie pulsu PMT", time_arr, value_arr, sample_signal, sample_sizes, markers, A, sigma, tau, start_time, stop_time, 1)
    plot_sampled_signal("Próbkowanie ADC 8-bit", time_arr, value_arr, sample_signal_ADC_8_bit, sample_sizes, markers, A, sigma, tau, start_time, stop_time, 2)
    plot_sampled_signal("Próbkowanie ADC 12-bit", time_arr, value_arr, sample_signal_ADC_12_bit, sample_sizes, markers, A, sigma, tau, start_time, stop_time, 3)
    
    plt.show()

    # Całkowanie funkcji
    result, error = spi.quad(lambda t: exp_PMT_pulse_fun(t, A, sigma, tau), start_time, stop_time)
    print("Całka z funkcji: ", result)
    print("Oszacowany błąd: ", error)

if __name__ == "__main__":
    main()
