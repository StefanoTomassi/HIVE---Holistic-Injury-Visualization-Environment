import os
import numpy as np
import matplotlib.pyplot as plt
import Strain_limits_and_ROM
from get_IV_NIC import get_IV_NIC, get_SA_nodes, get_SA_nodes, get_dynamic_theta, plot_kinematic, plot_IV_NIC
from history_node_id import write_node_id as hnid
from keyword_reader import read_keywords as rk
from dataviz_criteria_creation import create_dataviz_criteria as cdc
import directories_files

    
cwd = os.path.normpath(os.getcwd() + os.sep + os.pardir)
input_dir_auxiliaries = os.path.join(cwd, r"Data_generation\results_and_file_definition")
input_dir_sim = os.path.join(cwd, r"Data_generation\results_and_file_definition")
output_dir = os.path.join(cwd, r"Data_generation\results")

file_dir = directories_files.keyword_dir
print(f"Reading file: {file_dir}")
cards = rk(file_dir)
for card in cards:
    if 'DATABASE_HISTORY_NODE_ID' in card:
        print(f'Keyword: {card}')
        node_dict = hnid(cards[card])
        #cdc(node_dict, x_crit="x_coordinate", y_crit="z_coordinate")

ids = np.loadtxt('results/x_coordinates.csv', delimiter=',', max_rows=1, dtype=int)
x_coordinate = np.loadtxt('results/x_coordinates.csv',
                        delimiter=',', skiprows=1, dtype=float)
z_coordinate = np.loadtxt('results/z_coordinates.csv',
                    delimiter=',', skiprows=1, dtype=float)
time = np.loadtxt('results/time.csv',
                    delimiter=' ', dtype=float)

SA_nodes, SAx_coordinates = get_SA_nodes(node_dict, criteria='SA', coordinates=x_coordinate, ids=ids)
SA_nodes, SAz_coordinates = get_SA_nodes(node_dict, criteria='SA', coordinates=z_coordinate, ids=ids)
OC_nodes, OCx_coordinates = get_SA_nodes(node_dict, criteria='OC', coordinates=x_coordinate, ids=ids)
OC_nodes, OCz_coordinates = get_SA_nodes(node_dict, criteria='OC', coordinates=z_coordinate, ids=ids)
Cx_coordinates = np.concatenate((OCx_coordinates, SAx_coordinates), axis=1)
Cz_coordinates = np.concatenate((OCz_coordinates, SAz_coordinates), axis=1)
print("Cx_coordinates shape:", Cx_coordinates.shape)
n_seg = Cx_coordinates.shape[1]-1   # 7 segments: C0-C1, C1–C2, C2–C3, ..., C7–T1
theta_dynamic_segments = []
for j in range(n_seg):
    upx = Cx_coordinates[:, j+1]      # upper vertebra (C(j+1))
    upz = Cz_coordinates[:, j+1]
    lowx = Cx_coordinates[:, j]       # lower vertebra (Cj)
    lowz = Cz_coordinates[:, j]
    theta = get_dynamic_theta(upx, upz, lowx, lowz)
    theta_dynamic_segments.append(theta)
theta_dynamic_segments = np.array(theta_dynamic_segments)
for theta,ROM,ROM_label in zip(theta_dynamic_segments, Strain_limits_and_ROM.ROMs, Strain_limits_and_ROM.ROM_labels):
    IV_NIC = get_IV_NIC(theta, ROM)
    plot_IV_NIC(time, IV_NIC, ROM,ROM_label)
    if max(IV_NIC) > 0.75 or min(IV_NIC) < -1:
        max_IV_NIC = max(IV_NIC)
        time_of_max_IV_NIC = time[np.argmax(IV_NIC)]
        print(f"Warning: IV_NIC exceeds limits for {ROM_label}. Max IV_NIC: {max_IV_NIC:.2f} at time {time_of_max_IV_NIC:.2f} ms")
        plot_kinematic(Cx_coordinates, Cz_coordinates, IV_NIC, ROM_label)



