#Import of libraries
import numpy as np
import pyvista as pv
import lsreader as lr
from pathlib import Path
import os 
import sys
import imageio


#Import the paths
current_dir = Path(__file__).resolve().parent
upper_dir = current_dir.parent
sys.path.append(str(upper_dir))
from get_components import get_component
from get_points import get_points
from get_cells import get_cells
from directories_files import d3plot_dir_list, nodes_dir, part_dir
from get_elements_from_keyword import get_elements_from_keyword as shells_from_keyword
from get_strain import get_strain


#Reading the d3plot file
dr = lr.D3plotReader(d3plot_dir_list[0])
p = lr.D3P_Parameter()
p.ist = 0  # Timestep
p.ipt = 1  # Integration point (0=top, 1=middle, 2=bottom)
p.ipart_user = 2004110  # Part ID (0 for all parts, or specify a part ID)
num_states = dr.get_data(lr.DataType.D3P_NUM_STATES)
shells, parts = shells_from_keyword(nodes_dir, part_dir)
selected_part = 'N_L_AOCJ-CL'
nodes, points_with_id = get_points(dr, p)
shells_in_part, nodes, nodes_with_id = get_component(points_with_id, shells, parts, selected_part)

#Get simulation time steps and print info about the simulation time
times = []
for i in range(num_states):
    time_vec = dr.get_data(lr.DataType.D3P_TIMES, ist=i)
    times.append(float(time_vec[i]))  # or time_vec.get_value(0)
times = np.array(times)
print(f"Times: {times[0]:.4f} → {times[-1]:.4f}s ({len(times)} states)")
print(f"Total timesteps: {num_states}")

shell_ids = np.array(dr.get_data(lr.DataType.D3P_SHELL_IDS, ist=0))

pl = pv.Plotter()
pl.open_movie('animation_3.mp4', framerate=10)

#Initial frame setup


cells, cell_types = get_cells(dr, p, nodes_with_id, shells_in_part)
strain = get_strain(dr,p,shells_in_part)
mesh = pv.UnstructuredGrid(cells, cell_types, nodes)
print("Cells shape:", cells.shape, "Cell types shape:", cell_types.shape, "Nodes shape:", nodes.shape, "Strain shape:", strain.shape)
mesh.cell_data['plastic_strain'] = strain
actor = pl.add_mesh(mesh, scalars = 'plastic_strain', color='green', render_points_as_spheres=False, show_edges=True,  show_scalar_bar=True)
pl.add_text(f'Time: {times[0]:.4f}s', position='upper_left', font_size=12, color='white')
pl.write_frame()  # Write the first frame


for i in range(1, num_states):
    print(f"Processing frame {i+1}/{num_states} (Time: {times[i]:.4f}s)")
    p.ist = i  # Timestep
    points, points_with_id = get_points(dr, p)
    shells_in_part, nodes, nodes_with_id = get_component(points_with_id, shells, parts, selected_part)
    cells, cell_types = get_cells(dr, p, nodes_with_id, shells_in_part)
    new_mesh = pv.UnstructuredGrid(cells, cell_types, nodes)
    new_mesh.cell_data['plastic_strain'] = get_strain(dr,p,shells_in_part)
    pl.remove_actor(actor)
    actor = pl.add_mesh(new_mesh, scalars = 'plastic_strain', color='green', render_points_as_spheres=False, show_edges=True,  show_scalar_bar=True)
    pl.add_text(f'Time: {times[i]:.4f}s', position='upper_left', font_size=12, color='white')
    pl.reset_camera()
    pl.write_frame()  # Write each frame in the loop

pl.close()