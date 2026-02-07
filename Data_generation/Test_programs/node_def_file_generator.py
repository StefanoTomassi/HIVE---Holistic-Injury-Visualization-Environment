import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from history_node_id import write_node_id as hnid
from keyword_reader import read_keywords as rk
from dataviz_criteria_creation import create_dataviz_criteria as cdc

file_dir = r'C:\Users\d069056\OneDrive - Politecnico di Torino\File di Alessandro  Scattina - S361385_TOMASSI_Stefano\Modelli\Ettore_whiplash\2023_02_23_HN_sim_03\extensionWhiplashSimulation-main\umat41\0deg\run.key'
cards = rk(file_dir)
for card in cards:
    if 'DATABASE_HISTORY_NODE_ID' in card:
        print(f'Keyword: {card}')
        node_dict = hnid(cards[card])
        cdc(node_dict)