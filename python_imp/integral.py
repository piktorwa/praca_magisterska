# Author: Witkor Pantak
# Date: 2025-03-27
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: In this file is implemented the integral function.


def integrate_rectangle_method(t_samples, y_samples): # Rectangle method
    """
    Calculate integral using rectangle method from sampled data.
    
    Args:
        t_samples: array of time values
        y_samples: array of corresponding function values
        
    Returns:
        integral value
    """
    integral = 0.0
    for i in range(len(t_samples) - 1):
        dt = t_samples[i + 1] - t_samples[i]
        integral += y_samples[i] * dt       
    return integral

def calculate_error(approx_value, reference_value):
    """
    Calculate absolute and relative error compared to reference value.
    
    Args:
        approx_value: approximated value
        reference_value: reference (exact) value
        
    Returns:
        (absolute_error, relative_error) tuple
    """
    absolute_error = abs(approx_value - reference_value)
    relative_error = absolute_error / abs(reference_value) * 100  # in percent
    return absolute_error, relative_error