import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))
from find_simulation_files import find_output_simulation_files as find_files


Whiplash_example_dir = r'C:\Users\d069056\Desktop\git\output_data\Whiplash_example'
binout_dir, d3plot_dir_list = find_files(Whiplash_example_dir)            
keyword_dir = Whiplash_example_dir + r'\run.key'  
nodes_dir = r'C:\Users\d069056\Desktop\git\output_data\Whiplash_example\VIVA_OpenHBM_F50_Geom_20161202_HN_only.key'