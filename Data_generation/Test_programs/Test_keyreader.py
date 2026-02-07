import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import keyword_reader as kr
file_dir = r'C:\Users\d069056\OneDrive - Politecnico di Torino\File di Alessandro  Scattina - S361385_TOMASSI_Stefano\Modelli\Ettore_whiplash\2023_02_23_HN_sim_03\extensionWhiplashSimulation-main\umat41\0deg\run.key'
cards = kr.read_keywords(file_dir)
for card in cards:
    print(f'Keyword: {card}')
    for line in cards[card]:
        print(line.strip())