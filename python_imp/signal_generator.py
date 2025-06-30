# Author: Witkor Pantak
# Date: 2025-04-04
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: File contains functions for generating signals and sampling them.

import math as m
import numpy as np
import scipy.integrate as spi

def exp_PMT_pulse_fun(t, A, sigma, tau):
    '''
    Exponential PMT pulse function.
    Args:       t: time variable
                A: amplitude of the pulse
                sigma: rising time variable of the pulse
                tau: falling time variable of the pulse
    '''
    C = m.exp(-0.5 * (sigma * tau) * (sigma * tau))  # normalization constant
    th = 2 * sigma * sigma / tau  # threshold time

    if t <= th:
        return A * m.exp(-0.5 * (t / sigma) * (t / sigma))
    else:
        return A / C * m.exp(-1.0 * (t / tau))

def PMT_pulse_values(start_time, stop_time, time_step, A, sigma, tau):
    '''
    Generate the time and value arrays for the PMT pulse.
    Args:       start_time: start time of the pulse
                stop_time: stop time of the pulse
                time_step: time step for the pulse
                A: amplitude of the pulse
                sigma: rising time variable of the pulse
                tau: falling time variable of the pulse
    '''
    time_arr = np.arange(start_time, stop_time, time_step, dtype=float)
    value_arr = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in time_arr])
    return time_arr, value_arr

def sample_signal(start_time, stop_time, num_samples, A, sigma, tau):
    '''
    Sampling function for ideal ADC.
    Args:       start_time: start time of the sampling
                stop_time: stop time of the sampling
                num_samples: number of samples to generate
                A: amplitude of the pulse
                sigma: rising time variable of the pulse
                tau: falling time variable of the pulse
    '''
    t_samples = np.linspace(start_time, stop_time, num_samples)
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    return t_samples, y_samples

def sample_signal_ADC_n_bit(start_time, stop_time, num_samples, A, sigma, tau, n_bit, A_max = 2.0):
    '''
    Sampling function for n-bit ADC with quantization to n-bit levels.
    Args:       start_time: start time of the sampling
                stop_time: stop time of the sampling
                num_samples: number of samples to generate
                A: amplitude of the pulse
                sigma: rising time variable of the pulse
                tau: falling time variable of the pulse
                n_bit: number of bits for ADC
                A_max: maximum amplitude for quantization
    '''

    t_samples = np.linspace(start_time, stop_time, num_samples)
    step = A_max / 2**n_bit  # n-bit ADC step size
    y_samples = np.array([exp_PMT_pulse_fun(t, A, sigma, tau) for t in t_samples])
    y_samples = np.round(y_samples / step) * step # Quantize to n-bit levels
    return t_samples, y_samples

def sample_signal_ADC_n_bit_ver_2(t_samples, y_samples, n_bit, A = 2.0):
    '''
    Sampling function for n-bit ADC with quantization to n-bit levels.
    Args:       t_samples: array of time samples
                y_samples: array of signal samples
                n_bit: number of bits for ADC
                A: maximum amplitude for quantization
    '''
    step = A / 2**n_bit  # n-bit ADC step size
    y_samples_n_bit = np.round(y_samples / step) * step # Quantize to n-bit levels
    return t_samples, y_samples_n_bit

def integrate_PMT_pulse(A, sigma, tau, start_time, stop_time):
    '''
    Integrate the PMT pulse function over a specified time range.
    Args:       A: amplitude of the pulse
                sigma: rising time variable of the pulse
                tau: falling time variable of the pulse
                start_time: start time of the integration
                stop_time: stop time of the integration
    '''
    result, error = spi.quad(lambda t: exp_PMT_pulse_fun(t, A, sigma, tau), start_time, stop_time)
    return result, error