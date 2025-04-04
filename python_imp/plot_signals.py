# Author: Witkor Pantak
# Date: 2025-04-04
# Version: 1.0
# AGH University of Science and Technology, Cracov
# Description: File contains functions for plotting signals and their interpolations.

import matplotlib.pyplot as plt

def plot_sampled_signal(title, time_arr, value_arr, t_samples_list, y_samples_list, labels, fig_num): # Plotting function
    plt.figure(fig_num)
    plt.plot(time_arr, value_arr, label="Puls z fotopowielacza")

    markers = ['o', 's', 'D']  # Different markers for different sample sizes
    
    for i, (t_samples, y_samples) in enumerate(zip(t_samples_list, y_samples_list)):
        plt.plot(t_samples, y_samples, marker=markers[i], linestyle='', label=labels[i])

    plt.xlabel("Czas (s)")
    plt.ylabel("Amplituda [V]")
    plt.title(title)
    plt.legend()
    plt.grid()

def plot_interpolated_signal(title, time_arr, value_arr, t_samples, y_samples, t_interpolated, y_interpolated, sample_label, fig_num): # Plotting function for interpolated signal
    plt.figure(fig_num)
    plt.plot(time_arr, value_arr, 'b-', label="Puls z fotopowielacza")
    
    # Plot sample points
    plt.plot(t_samples, y_samples, 'ro', markersize=6, label=f"{sample_label}")
    
    # Plot interpolated signal
    plt.plot(t_interpolated, y_interpolated, 'gx', label="Interpolacja liniowa")
    
    plt.xlabel("Czas (s)")
    plt.ylabel("Amplituda [V]")
    plt.title(title)
    plt.legend()
    plt.grid()