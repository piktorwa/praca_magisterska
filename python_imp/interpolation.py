# Author: Witkor Pantak
# Date: 2025-04-03
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: File contains functions for interpolation of sampled data.

import numpy as np
from scipy.interpolate import CubicSpline

new_samples = 10 # Number of new samples for interpolation

def linear_interpolation(t_samples, y_samples):
    """
    Perform linear interpolation between sampled data points.
    
    Args:
        t_samples: array of time values
        y_samples: array of corresponding function values
        
    Returns:
        interpolated time and value arrays
    """
    t_interpolated = np.linspace(t_samples[0], t_samples[-1], len(t_samples) * new_samples)  # n times more points for interpolation
    y_interpolated = np.interp(t_interpolated, t_samples, y_samples)
    return t_interpolated, y_interpolated

def cubic_spline_interpolation(t_samples, y_samples):
    """
    Perform cubic spline interpolation between sampled data points.
    
    Args:
        t_samples: array of time values
        y_samples: array of corresponding function values
        
    Returns:
        interpolated time and value arrays
    """
        
    cs = CubicSpline(t_samples, y_samples)
    t_interpolated = np.linspace(t_samples[0], t_samples[-1], len(t_samples) * new_samples)  # n times more points for interpolation
    y_interpolated = cs(t_interpolated)
    return t_interpolated, y_interpolated

def polynomial_interpolation(t_samples, y_samples, degree, check = True):
    """
    Perform polynomial interpolation between sampled data points.
    
    Args:
        t_samples: array of time values
        y_samples: array of corresponding function values
        degree: degree of the polynomial to fit
        
    Returns:
        interpolated time and value arrays
    """
    coeffs = np.polyfit(t_samples, y_samples, degree)
    poly = np.poly1d(coeffs)
    t_interpolated = np.linspace(t_samples[0], t_samples[-1], len(t_samples) * new_samples)  # n times more points for interpolation
    y_interpolated = poly(t_interpolated)
    if check: return t_interpolated, y_interpolated
    else: 
        t_interpolated = t_interpolated[new_samples:-new_samples-1]  # Remove first n and last n points to avoid edge effects
        y_interpolated = y_interpolated[new_samples:-new_samples-1]  # Remove first n and last n points to avoid edge effects
        return t_interpolated, y_interpolated