# Author: Witkor Pantak
# Date: 2025-04-04
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: File contains functions for generating signals and sampling them.

import math as m
import numpy as np
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

def sample_signal(start_time, stop_time, num_samples, A, sigma, tau): # Sampling function for ideal ADC
    t_samples = np.linspace(start_time, stop_time, num_samples)
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    return t_samples, y_samples

def sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, n_bit): # Sampling function for n-bit ADC
    t_samples = np.linspace(start_time, stop_time, num_samples)
    step = A / 2**n_bit  # n-bit ADC step size
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    y_samples = np.round(y_samples / step) * step # Quantize to n-bit levels
    return t_samples, y_samples

def integrate_PMT_pulse(A, sigma, tau, start_time, stop_time): # Integrate the PMT pulse function over a specified time range
    result, error = spi.quad(lambda t: exp_PMT_pulse_fun(t, A, sigma, tau), start_time, stop_time)
    return result, error