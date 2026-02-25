#Import of libraries
import numpy as np
import pyvista as pv
import lsreader as lr
from pathlib import Path
import os 
import sys

#Import the paths
current_dir = Path(__file__).resolve().parent
upper_dir = current_dir.parent
sys.path.append(str(upper_dir))
from get_points import get_points
from get_cells import get_cells
from directories_files import d3plot_dir_list

#Reading the d3plot file
dr = lr.D3plotReader(d3plot_dir_list[0])
num_states = dr.get_data(lr.DataType.D3P_NUM_STATES)

#Get simulation time steps and print info about the simulation time
times = []
for i in range(num_states):
    time_vec = dr.get_data(lr.DataType.D3P_TIMES, ist=i)
    times.append(float(time_vec[i]))  # or time_vec.get_value(0)
times = np.array(times)
print(f"Times: {times[0]:.4f} → {times[-1]:.4f}s ({len(times)} states)")
print(f"Total timesteps: {num_states}")

shell_ids = np.array(dr.get_data(lr.DataType.D3P_SHELL_IDS, ist=i, ipt=1))
pl = pv.Plotter()

#Extracting the coordinates of the nodes at the last time step
p = lr.D3P_Parameter()
p.ist = 0  # Timestep
p.ipt = 1  # Integration point (0=top, 1=middle, 2=bottom)
points, points_with_id = get_points(dr, p)
cells, cell_types = get_cells(dr, p, points_with_id)

mesh = pv.UnstructuredGrid(cells, cell_types, points)
pl.add_mesh(mesh, color='green', render_points_as_spheres=False, show_edges=True)
pl.show()
