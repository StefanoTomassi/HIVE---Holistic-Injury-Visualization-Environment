import os
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))
from find_simulation_files import find_output_simulation_files as find_files
from select_folder import choose_file, choose_file, choose_folder

Whiplash_example_dir = choose_folder("Select folder with simulation results")
d3plot = os.path.join(Whiplash_example_dir, "d3plot")
binout_dir, d3plot_dir_list = find_files(Whiplash_example_dir)            
keyword_dir = Whiplash_example_dir + r'\run.key'  
#nodes_dir = choose_file("Select nodes file", filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")))
#part_dir = choose_file("Select part file", filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")))