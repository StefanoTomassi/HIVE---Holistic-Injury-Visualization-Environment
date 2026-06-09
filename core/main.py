import dataclasses.simulation_dataclasses as DataClass
import object_file_generation as wf
#import process_whiplash_simulation as process_whiplash_simulation
def main():

    choice = str(input("Select simulation type (e.g., 'Whiplash'):"))
    wf.write_file_generation(choice)
    if choice == 'Whiplash':
        # Call the function to process whiplash simulation data
        simulation_data = DataClass.SimulationData(name="Whiplash",
             output_dir=None,
             database_file=None,
             criteria=[{'node': ['x_displacement',
                        'z_displacement',
                        'x_velocity',
                        'z_velocity',
                        'x_acceleration',
                        'z_acceleration']
                        }],
                        
             mesh_file=None, 
             part_file=None)
        process_whiplash_simulation(simulation_data)
    if choice == 'global':
        simulation_data = DataClass.SimulationData(name="Global",
             output_dir=None,
            database_file=None,
            mesh_file=None,
            part_file=None)