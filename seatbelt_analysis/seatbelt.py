import json
import os
import pandas as pd
from dynasaur.plugins.data_visualization_controller import DataVisualizationController
from dynasaur.plugins.criteria_controller import CriteriaController
from dynasaur.data.ls_dyna import EloutObject
import csv
#Import of custom functions
import core.io.keyword_reader as kr
import core.io.create_criteria as cc
import core.io.create_objects as co
from core.io.select_folder import choose_folder, choose_file
import core.io.directories_files as directories_files
import sys
from pathlib import Path
from seatbelt_analysis.get_seatbelt_commands import get_seatbelt_commands
from seatbelt_analysis.plot_seatbelt import plot_seatbelt_measurements as plot_seatbelt
def main():
    simulation_files_dir = choose_folder("Select folder with simulation files and auxiliary files (def files)")
    output_dir = choose_folder("Select folder to save results in .csv format")
    cards = kr.read_keywords(choose_file("Select keyword file", filetypes=(("Keyword files", "*.k*"), ("All files", "*.*"))))
    simulation_type = input("Enter simulation type (e.g., 'whiplash'):")
    path_to_def = os.path.join(simulation_files_dir, "criteria_definition_" + simulation_type + ".def")
    path_to_def_id = os.path.join(simulation_files_dir, "object_definition_" + simulation_type + ".def")
    path_to_data = os.path.join(simulation_files_dir, "binout*")
    all_objects = []
    all_data_visualization = []
    seatbelts, retractors, sliprings, pretensioners = kr.get_dyna_seatbelt(cards)
    seatbelts_objects = co.create_objects(type_obj="SEAT_BELT", data=seatbelts)
    retractors_objects = co.create_objects(type_obj="RETRACTOR", data=retractors)
    sliprings_objects = co.create_objects(type_obj="SLIP_RING", data=sliprings)
    all_objects.extend(seatbelts_objects)
    all_objects.extend(retractors_objects)
    all_objects.extend(sliprings_objects)
    co.write_object_file(dir=path_to_def_id, objects=all_objects)
    seatbelt_data_visualization, seatbelt_data_visualizations_definitions = get_seatbelt_commands(sliprings, retractors, seatbelts)
    all_data_visualization.extend(seatbelt_data_visualizations_definitions)
    cc.write_criteria_file(dir=path_to_def, data_visualization=all_data_visualization, criteria=[])
    data_vis_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)

    for seatbelt in seatbelt_data_visualization:
        command = {'visualization': seatbelt.part_of+'_'+seatbelt.name, 'x_label': seatbelt.x+' [ms]', 'y_label': seatbelt.y+' [J]'}
        print(command)
        data_vis_controller.calculate(command)
    
    data_vis_controller.write_CSV(output_dir, filename="seatbelt_data.csv")
    plot_seatbelt(csv_path=os.path.join(output_dir, "seatbelt_data.csv"))
if __name__ == "__main__":
    main()
