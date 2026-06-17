import os
import glob
import json
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
from global_energy.get_global_commands import get_global_commands as get_global_energy_commands
from global_energy.get_global_energies import plot_global_energy_timeseries
from global_energy.get_part_commands import get_part_commands
from global_energy.get_part_energies import plot_part_energy_timeseries
from global_energy.get_other_energies_commands import get_other_energies_commands
from global_energy.get_other_energies import plot_other_energy_timeseries
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
    global_energy_objects = co.create_objects(type_obj="ENERGY_GLOBAL", data={"Model": "0"})
    all_objects.extend(global_energy_objects)


    parts= kr.get_dyna_parts(cards)
    part_objects = co.create_objects(type_obj="ENERGY_PART", data=parts)
    all_objects.extend(part_objects)
    parts_def = []
    for part in parts:  
        parts_def_iter, part_energy_definitions = get_part_commands(part)
        parts_def.extend(parts_def_iter)
        all_data_visualization.extend(part_energy_definitions)
    joints = kr.get_dyna_joints(cards)
    joints_objects = co.create_objects(type_obj="JOINT", data = joints)
    all_objects.extend(joints_objects)
    boundaries = kr.get_dyna_boundary_motions(cards)
    boundaries_objects = co.create_objects(type_obj="BOUNDARY_CONDITION", data = boundaries)
    all_objects.extend(boundaries_objects)
    contacts = kr.get_dyna_contact(cards)
    contacts_objects = co.create_objects(type_obj="SLEOUT", data = contacts)
    all_objects.extend(contacts_objects)
    other_energy_definitions, other_energy_data_definitions = get_other_energies_commands(boundaries, joints, contacts)
    co.write_object_file(dir=path_to_def_id, objects=all_objects)
    global_energy, global_energy_definitions = get_global_energy_commands()
    all_data_visualization.extend(global_energy_definitions)
    all_data_visualization.extend(other_energy_data_definitions)

    cc.write_criteria_file(dir=path_to_def, data_visualization=all_data_visualization, criteria=[])   
    global_energy_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)
    part_energy_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)
    other_energy_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)
    for energy in global_energy:
        command = {'visualization': energy.part_of+'_'+energy.name, 'x_label': energy.x+' [ms]', 'y_label': energy.y+' [J]'}
        global_energy_controller.calculate(command) 
    global_energy_controller.write_CSV(output_dir, filename="global_energies.csv")

    for part in parts_def:
        command = {'visualization': part.part_of+'_'+part.name, 'x_label': part.x+' [ms]', 'y_label': part.y+' [J]'}
        part_energy_controller.calculate(command)
    part_energy_controller.write_CSV(output_dir, filename="part_energies.csv")

    for energy in other_energy_definitions:
        command = {'visualization': energy.part_of+'_'+energy.name, 'x_label': energy.x+' [ms]', 'y_label': energy.y+' [J]'}
        other_energy_controller.calculate(command)
    other_energy_controller.write_CSV(output_dir, filename="other_energies.csv")
    
    

    fig, summary_df, percentage_table_glob = plot_global_energy_timeseries(csv_path=os.path.join(output_dir, "global_energies.csv"))
    fig, summary_df, percentage_table_part = plot_part_energy_timeseries(csv_path=os.path.join(output_dir, "part_energies.csv"))
    fig, summary_df, percentage_table_other = plot_other_energy_timeseries(csv_path=os.path.join(output_dir, "other_energies.csv"))
    percentage_table_glob.to_csv(os.path.join(output_dir, "percentage_table_global.csv"), index=False)
    percentage_table_part.to_csv(os.path.join(output_dir, "percentage_table_part.csv"), index=False)
    percentage_table_other.to_csv(os.path.join(output_dir, "percentage_table_other.csv"), index=False)

if __name__ == "__main__":
    main()

