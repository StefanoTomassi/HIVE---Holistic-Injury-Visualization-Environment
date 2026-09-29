from GUI.layout.Plots.signal_plots import (
    _measurement_figure,
    find_measurement_pairs,
    read_csv_data,
)

path = r"C:\Users\d069056\Desktop\git\output_data\Whiplash_example\whiplash_node_x_acceleration.csv"
signal_data = read_csv_data(None, path)
pair = find_measurement_pairs(signal_data)[0]
figure = _measurement_figure([(signal_data, pair[0], pair[1])])

figure.show()