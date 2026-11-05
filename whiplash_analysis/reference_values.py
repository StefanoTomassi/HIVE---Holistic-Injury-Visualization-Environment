#Ligaments strain limits coming from Yonagandan et al, 2000

cervical_ligament_strain_limits = {'ALL_strain_limits_C2C5' : [25.8, 30.8, 35.8], 'PLL_strain_limits_C2C5' : [15, 18.2, 21.4], 'CL_strain_limits_C2C5' : [120, 148.5, 176.5],
           'LF_strain_limits_C2C5' : [64.1, 77, 89.9], 'ISL_strain_limits_C2C5' : [59.7, 60.9, 72.1], 'ALL_strain_limits_C5T1' : [29.54, 35.4, 41.26],
            'PLL_strain_limits_C5T1' : [25.33, 34.1, 42.87], 'CL_strain_limits_C5T1' : [96.4, 116, 135.6], 'LF_strain_limits_C5T1' : [75.3, 88.4, 101.5],
            'ISL_strain_limits_C5T1' : [54.3, 68.1, 81.9] }
   
#Ligamament strain limit from Mattucci et al, 2011

craniovertebral_ligament_strain_limits = {'AAAM': [0.53, 0.53, 0.53], 'PAAM': [0.49, 0.49, 0.49], 'AAOM': [0.36, 0.46, 0.56], 
                                          'PAOM': [0.39, 0.52, 0.65], 'TL': [24.8, 25.4, 26], 'TM_Complex': [0.33, 0.43, 0.53] }

#Range of motion present in Panjabi et al. 1999

ROM_C0C1 = [-13.6, 13.85]
ROM_C1C2 = [-7.818, 12.842]
ROM_C2C3 = [-4.988, 4.847]
ROM_C3C4 = [-5.625, 6.509]
ROM_C4C5 = [-5.342, 6.616]
ROM_C5C6 = [-7.889, 7.11]
ROM_C6C7 = [-4.599, 6.439]
ROM_C7T1 = [-2.476, 4.281]
ROMs = [ROM_C0C1, ROM_C1C2, ROM_C2C3, ROM_C3C4, ROM_C4C5, ROM_C5C6, ROM_C6C7, ROM_C7T1]
ROM_labels = ['C1-C2', 'C2-C3', 'C3-C4', 'C4-C5', 'C5-C6', 'C6-C7', 'C7-T1']
Spine_labels = [ 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1']

# Load and energy limits in facet joints from Yonagandan et al. 1989

facet_joint_trauma_limits = {'load': [9000, 4400], 'energy': [10.2, 5.8]}
facet_joint_failure_limits = {'load': [11000, 5300], 'energy': [18.0, 5.7]}

#Muscular force limits from Martynenko et al. 2023
sigma_max_muscle = 0.5e-3 #GPa

#Intervertebral disc strain limits from Yonagandan et al. 1996

intervertebral_discs_energy_limits = {'C2C3': 3.7, 'C3C4': 4.4, 'C4C5': 5.5, 'C5C6': 2.6, 'C6C7': 3.3, 'C7T1': 3.3}
intervertebral_discs_force_limits = {'C2C3': 636, 'C3C4': 590, 'C4C5': 571, 'C5C6': 391, 'C6C7': 505, 'C7T1': 510}
