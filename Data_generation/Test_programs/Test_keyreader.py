import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keyword_reader import read_keywords as kr
from keyword_reader import get_dyna_parts as gdp
from keyword_reader import get_selected_part as gsp
file_dir = r'C:\Users\d069056\OneDrive - Politecnico di Torino\File di Alessandro  Scattina - S361385_TOMASSI_Stefano\Modelli\Ettore_whiplash\2023_02_23_HN_sim_03\extensionWhiplashSimulation-main\umat41\0deg\run.key'
cards = kr(file_dir)
file_parts = r'C:\Users\d069056\Desktop\git\output_data\Whiplash_example\VIVA_OpenHBM_F50_HN_Part_Data_20160620.key'
cards_parts = kr(file_parts)
for card in cards_parts:
    if 'PART' in card:
        print(f'Keyword: {card}', f'Lines: {cards_parts[card]}')
parts = gdp(cards_parts)
print(parts)
part_list = gsp('ISL',parts)
print(part_list) 