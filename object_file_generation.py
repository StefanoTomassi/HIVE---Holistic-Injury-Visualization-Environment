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
from global_energy.get_global_energies import plot_all_timeseries
def main():

    simulation_files_dir = choose_folder("Select folder with simulation files and auxiliary files (def files)")
    output_dir = choose_folder("Select folder to save results in .csv format")
    cards = kr.read_keywords(choose_file("Select keyword file", filetypes=(("Keyword files", "*.k*"), ("All files", "*.*"))))
    simulation_type = input("Enter simulation type (e.g., 'whiplash'):")
    path_to_def = os.path.join(simulation_files_dir, "criteria_definition_" + simulation_type + ".def")
    path_to_def_id = os.path.join(simulation_files_dir, "object_definition_" + simulation_type + ".def")
    path_to_data = os.path.join(simulation_files_dir, "binout*")
    #all_data_visualization = []
    #for card in cards:
        #if 'PART' in card:
            #node_dict = kr.get_dyna_history_id(cards[card])
            #node_objects = co.create_objects(type_obj="NODE", data=node_dict)
            #all_objects.extend(node_objects)
            #node_data = cc.create_data_visualization(name=simulation_type, data=node_dict, crit_type="NODE", x_crit="time", y_crit="y_coordinate")
            #all_data_visualization.extend(node_data)
            #   commands = [{'visualization': node+'_'+simulation_type, 'x_label': 'time', 'y_label': 'y_coord'} for node in node_dict]
        #if 'DATABASE_HISTORY_SHELL_ID' in card:
            #shell_dict = kr.get_dyna_history_id(cards[card])
            #shell_objects = co.create_objects(type_obj="ELEMENT", data=shell_dict)
            #all_objects.extend(shell_objects)
            #shell_data = cc.create_data_visualization(name=simulation_type, data=shell_dict, crit_type="ELEMENT", x_crit="time", y_crit="upper_max_principal_strain")
            #all_data_visualization.extend(shell_data)
            #commands += [{'visualization': shell+'_'+simulation_type, 'x_label': 'time', 'y_label': 'upper_max_principal_strain'} for shell in shell_dict]
        #if 'DATABASE_HISTORY_SOLID_ID' in card:
            #solid_dict = kr.get_dyna_history_id(cards[card])
            #print(solid_dict)
            #solid_objects = co.create_objects(type_obj="ELEMENT", data=solid_dict)
            #all_objects.extend(solid_objects)
            #solid_data = cc.create_data_visualization(name=simulation_type, data=solid_dict, crit_type="ELEMENT", x_crit="time", y_crit="max_principal_strain")
            #all_data_visualization.extend(solid_data)
            #commands += [{'visualization': solid+'_'+simulation_type, 'x_label': 'time', 'y_label': 'max_principal_strain'} for solid in solid_dict]
        #if 'DATABASE_HISTORY_BEAM_ID' in card:
            #beam_dict = kr.get_dyna_history_id(cards[card])
            #beam_objects = co.create_objects(type_obj="ELEMENT", data=beam_dict)
            #all_objects.extend(beam_objects)
            #beam_data = cc.create_data_visualization(name=simulation_type, data=beam_dict, crit_type="ELEMENT", x_crit="time", y_crit="torsion")
            #all_data_visualization.extend(beam_data)
            #commands += [{'visualization': beam+'_'+simulation_type, 'x_label': 'time', 'y_label': 'torsion'} for beam in beam_dict]
    #open_criteria = cc.open_criteria_file(simulation_files_dir, simulation_type, all_criteria=all_criteria) #json.dump([], criteria, indent=2)
    
    #cc.write_criteria_file(dir=path_to_def, data_visualization=all_data_visualization, criteria=[])      
    all_objects = []
    energy_objects = co.create_objects(type_obj="ENERGY_GLOBAL", data={"Model": "0"})
    all_objects.extend(energy_objects)
    co.write_object_file(dir=path_to_def_id, objects=all_objects)    
        #if 'DATABASE_ELOUT' in card:
        #    part_dict = kr.get_dyna_parts(cards)
        #    co.write_part_obj(obj, part_dict)
    
    #cc.close_criteria_file(criteria) #json.dump(all_criteria, criteria, indent=2)
    print(all_objects)    
    
    global_energy, energy_definitions = get_global_energy_commands()
    cc.write_criteria_file(dir=path_to_def, data_visualization=energy_definitions, criteria=[])   
    data_vis_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)
    for energy in global_energy:
        print(energy)
        command = {'visualization': energy.part_of+'_'+energy.name, 'x_label': energy.x+' [ms]', 'y_label': energy.y+' [J]'}
        data_vis_controller.calculate(command)

    data_vis_controller.write_CSV(output_dir, filename="global_energies.csv")

    fig, summary_df, percentage_table = plot_all_timeseries(csv_path=os.path.join(output_dir, "global_energies.csv"))
    percentage_table.to_csv(os.path.join(output_dir, "percentage_table.csv"), index=False)
        #crit_controller = CriteriaController(calculation_procedure_def_file=path_to_def, object_def_file=path_to_def_id,
                                    #     data_source=path_to_data)

    #commands = [{'criteria': 'BOARD_solid_obj_1_stress'},
            #    {'criteria': 'BOARD_solid_obj_2_stress'},
             #   {'criteria': 'MODEL_Internal_Energy_Max'}]

    #for command in commands:
        #crit_controller.calculate(command)

    #crit_controller.write_CSV(output_dir, filename="criteria.csv")



if __name__ == "__main__":
    main()

