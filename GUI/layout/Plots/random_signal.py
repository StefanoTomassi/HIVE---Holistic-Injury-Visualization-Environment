from GUI.layout.Plots.signal_plots import plot_random_measurement

figure = plot_random_measurement(
    r"C:\Users\d069056\Desktop\git\output_data\Whiplash_example\whiplash_node_x_acceleration.csv",
    seed=7,
)

figure.show()