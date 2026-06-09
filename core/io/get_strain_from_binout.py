import os
import glob
import json
import pandas as pd
from dynasaur.plugins.data_visualization_controller import DataVisualizationController
from dynasaur.plugins.criteria_controller import CriteriaController
from dynasaur.data.ls_dyna import EloutObject, EloutIndex
import csv

#Import of custom functions
import keyword_reader as kr
import create_criteria as cc
import create_objects as co
from select_folder import choose_folder, choose_file
import directories_files as directories_files

def main():

    simulation_files_dir = choose_folder("Select folder with simulation files and auxiliary files (def files)")
    output_dir = choose_folder("Select folder to save results in .csv format")
    cards = kr.read_keywords(choose_file("Select keyword file", filetypes=(("Keyword files", "*.k*"), ("All files", "*.*"))))
    simulation_type = input("Enter simulation type (e.g., 'whiplash'):")
    path_to_def = os.path.join(simulation_files_dir, "criteria_definition_" + simulation_type + ".def")
    path_to_def_id = os.path.join(simulation_files_dir, "object_definition_" + simulation_type + ".def")
    path_to_data = os.path.join(simulation_files_dir, "binout*")
    all_data_visualization = []
    all_objects = []
    for card in cards:
        if 'DATABASE_HISTORY_SHELL_ID' in card:
            shell_dict = kr.get_dyna_history_id(cards[card])
            shell_objects = co.create_objects(type_obj="ELEMENT", data=shell_dict)
            print(shell_objects)
            print(shell_objects[0]['id'])
            elout_obj = EloutObject(path_to_data, None, shell_objects, volume_path=None)
            elout_obj.read_binout_data()
            index, data = elout_obj.get_part_data(EloutIndex.STRAIN, part_id)
        #if 'DATABASE_HISTORY_SOLID_ID' in card:
            #solid_dict = kr.get_dyna_history_id(cards[card])
            #print(solid_dict)
            #solid_objects = co.create_objects(type_obj="ELEMENT", data=solid_dict)
            #all_objects.extend(solid_objects)
            #solid_data = cc.create_data_visualization(name=simulation_type, data=solid_dict, crit_type="ELEMENT", x_crit="time", y_crit="max_principal_strain")
            #all_data_visualization.extend(solid_data)
            #commands += [{'visualization': solid+'_'+simulation_type, 'x_label': 'time', 'y_label': 'max_principal_strain'} for solid in solid_dict]
    #open_criteria = cc.open_criteria_file(simulation_files_dir, simulation_type, all_criteria=all_criteria) #json.dump([], criteria, indent=2)
    
    cc.write_criteria_file(dir=path_to_def, data_visualization=all_data_visualization, criteria=[])      
    co.write_object_file(dir=path_to_def_id, objects=all_objects)    
        #if 'DATABASE_ELOUT' in card:
        #    part_dict = kr.get_dyna_parts(cards)
        #    co.write_part_obj(obj, part_dict)
    
    #cc.close_criteria_file(criteria) #json.dump(all_criteria, criteria, indent=2)
    print(all_objects)
    data_vis_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)

    for command in commands:
        data_vis_controller.calculate(command)

    data_vis_controller.write_CSV(output_dir, filename="node_time_ycoordinate.csv")


if __name__ == "__main__":
    main()

