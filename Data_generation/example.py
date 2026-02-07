import os
import glob
import pandas as pd
from dynasaur.plugins.data_visualization_controller import DataVisualizationController
from dynasaur.plugins.criteria_controller import CriteriaController
import csv
from history_node_id import write_node_id as hnid
from keyword_reader import read_keywords as rk
from dataviz_criteria_creation import create_dataviz_criteria as cdc

def main():

    cwd = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    input_dir_auxiliaries = os.path.join(cwd, "Data/results_and_file_definition")
    input_dir_sim = os.path.join(cwd, "Data/results_and_file_definition")
    output_dir = os.path.join(cwd, "Data/results")

    path_to_def = os.path.join(input_dir_auxiliaries, "dataviz_criteria_2.def")
    path_to_def_id = os.path.join(input_dir_auxiliaries, "history_node_id_2.def")
    path_to_data = os.path.join(input_dir_sim, "binout*")

    data_vis_controller = DataVisualizationController(calculation_procedure_def_file=path_to_def,
                                                      object_def_file=path_to_def_id,
                                                      data_source=path_to_data)

    file_dir = r'C:\Users\d069056\OneDrive - Politecnico di Torino\File di Alessandro  Scattina - S361385_TOMASSI_Stefano\Modelli\Ettore_whiplash\2023_02_23_HN_sim_03\extensionWhiplashSimulation-main\umat41\0deg\run.key'
    cards = rk(file_dir)
    for card in cards:
        if 'DATABASE_HISTORY_NODE_ID' in card:
            print(f'Keyword: {card}')
            node_dict = hnid(cards[card])
            cdc(node_dict)

    commands = [{'visualization': node+'_xvel', 'x_label': 'time[ms]', 'y_label': 'x_vel'} for node in node_dict]    

    print(node_dict)
    for command in commands:
        data_vis_controller.calculate(command)

    data_vis_controller.write_CSV(output_dir, filename="node_xvel.csv")

    dataFrame = pd.read_csv(os.path.join(output_dir, "node_xvel.csv"), delimiter=';')
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

