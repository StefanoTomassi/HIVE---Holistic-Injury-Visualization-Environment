#Strain limits comign from Yonagandan et al, 2000
strain_limits = {'ALL_strain_limits_C2C5' : [25.8, 30.8, 35.8], 'PLL_strain_limits_C2C5' : [15, 18.2, 21.4], 'CL_strain_limits_C2C5' : [120, 148.5, 176.5],
           'LF_strain_limits_C2C5' : [64.1, 77, 89.9], 'ISL_strain_limits_C2C5' : [59.7, 60.9, 72.1], 'ALL_strain_limits_C5T1' : [29.54, 35.4, 41.26],
            'PLL_strain_limits_C5T1' : [25.33, 34.1, 42.87], 'CL_strain_limits_C5T1' : [96.4, 116, 135.6], 'LF_strain_limits_C5T1' : [75.3, 88.4, 101.5],
            'ISL_strain_limits_C5T1' : [54.3, 68.1, 81.9] }   
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