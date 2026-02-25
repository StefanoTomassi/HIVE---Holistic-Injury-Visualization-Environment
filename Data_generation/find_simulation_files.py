import os
import glob
from pathlib import Path
from typing import Tuple, Optional, List

def find_output_simulation_files(folder_path: str) -> Tuple[List[str], List[str]]:
    """
    Find binout files and d3plot series in given folder.
    
    Args:
        folder_path: Path to simulation folder
        
    Returns:
        Tuple of (sorted_binout_list, sorted_d3plot_list)
    """
    folder = Path(folder_path)
    
    # Find binout (exact name)
    binout_path = folder / r"binout*"
    binout_files = glob.glob(str(binout_path))
    if not binout_files:
        binout_path = None
    else:
        binout_path = binout_files[0]  # Use first found binout file
    
    # Sort naturally: d3plot, d3plot01, d3plot02...
    binout_files = sorted(binout_files, key=lambda x: (
        x.split('binout')[-1].zfill(10),  # Pad numbers
        x
    ))


    # Find all d3plot* files (base + d3plot01, d3plot02...)
    d3plot_pattern = folder / "d3plot*"
    d3plot_files = glob.glob(str(d3plot_pattern))
    
    if not d3plot_files:
        return binout_files, []
    
    # Sort naturally: d3plot, d3plot01, d3plot02...
    d3plot_files = sorted(d3plot_files, key=lambda x: (
        x.split('d3plot')[-1].zfill(10),  # Pad numbers
        x
    ))
    
    return binout_files, d3plot_files

# Usage examples
if __name__ == "__main__":
    # Current folder
    binout, d3plots = find_output_simulation_files(".")
    
    # Specific folder
    # binout, d3plots = find_output_simulation_files("/path/to/simulation")