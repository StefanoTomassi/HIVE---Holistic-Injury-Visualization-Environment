#Import of libraries
import numpy as np
import lsreader as lr
from pathlib import Path
import os 
import sys


#Import the paths
current_dir = Path(__file__).resolve().parent
upper_dir = current_dir.parent
sys.path.append(str(upper_dir))
from whiplash_analysis.get_visualization import get_component
from whiplash_analysis.get_visualization import get_points
from whiplash_analysis.get_visualization import get_cells
from core.io.directories_files import d3plot_dir_list, nodes_dir, part_dir
from whiplash_analysis.get_visualization import get_elements_from_keyword as shells_from_keyword
from whiplash_analysis.get_strain import get_strain, compute_max_strain, boxplot_strain
from core.io.keyword_reader import read_keywords as rk
from core.io.keyword_reader import get_dyna_parts as gdp
from core.io.keyword_reader import get_selected_part as gsp

cards = rk(part_dir)
parts = gdp(cards)
desired_parts = "LF"
parts_to_plot = gsp(desired_parts,parts)
print(parts_to_plot)
#Reading the d3plot file
dr = lr.D3plotReader(d3plot_dir_list[0])
p = lr.D3P_Parameter()
p.ist = 0  # Timestep
p.ipt = 1  # Integration point (0=top, 1=middle, 2=bottom)

#for part in parts_to_plot:
#    print(parts[part])
#    p.ipart_user = parts[part]
#    nodes, points_with_id = get_points(dr, p)
#    shells, parts = shells_from_keyword(nodes_dir, part_dir)
#    shells_in_part, nodes, nodes_with_id = get_component(points_with_id, shells, parts, part)
num_states = dr.get_data(lr.DataType.D3P_NUM_STATES)
#Get simulation time steps and print info about the simulation time
times = []
for i in range(num_states):
    time_vec = dr.get_data(lr.DataType.D3P_TIMES, ist=i)
    times.append(float(time_vec[i]))  # or time_vec.get_value(0)
times = np.array(times)
print(f"Times: {times[0]:.4f} → {times[-1]:.4f}s ({len(times)} states)")
print(f"Total timesteps: {num_states}")

shell_ids = np.array(dr.get_data(lr.DataType.D3P_SHELL_IDS, ist=0))

max_strains_in_comps = {}
for part_name in parts_to_plot:
    part_id = parts[part_name]
    print(part_id)          
    p.ipart_user = part_id
    p.ist = 0  # Timestep
    strain = get_strain(dr,p)
    max_strain = strain
    for i in range(1, num_states):
        p.ist = i  # Timestep
        strain = get_strain(dr,p)
        max_strain = compute_max_strain(strain, max_strain)
    max_strains_in_comps[part_name] =[max_strain]
print(max_strains_in_comps.keys())
boxplot_strain(max_strains_in_comps,desired_parts)