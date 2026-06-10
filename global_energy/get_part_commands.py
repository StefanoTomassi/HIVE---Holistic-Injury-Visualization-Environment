from core.dataclasses import simulation_dataclasses
from core.io.create_criteria import create_data_visualization

def get_part_commands(parts):
    for part in parts:
        InternalEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Internal Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="internal_energy",
                                                            x="time")
        KineticEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Kinetic Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="kinetic_energy",
                                                            x="time")
        HourglassEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Hourglass Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="hourglass_energy",
                                                            x="time")
        ErodedHourglassEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Eroded Hourglass Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="eroded_hourglass_energy",
                                                            x="time")
        ErodedKineticEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Eroded Kinetic Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="eroded_kinetic_energy",
                                                            x="time")
        ErodedInternalEnergy = simulation_dataclasses.DataVisualizationDefinition(name= part + " Eroded Internal Energy",
                                                            part_of= "Part Energy" + part,
                                                            type="ENERGY_PART",
                                                            ID= part,
                                                            y="eroded_internal_energy",
                                                            x="time")
    
    part_energies = [InternalEnergy, KineticEnergy, ErodedHourglassEnergy, ErodedKineticEnergy, ErodedInternalEnergy]
    
    part_energy_data_visualization = []
    for energy in part_energies:
        create_data_visualization(items = part_energy_data_visualization,
                                  name = energy.name,
                                  part_of = energy.part_of,
                                  ID = energy.ID,
                                  crit_type = energy.type,
                                  x_crit = energy.x,
                                  y_crit = energy.y)
     
    return part_energies, part_energy_data_visualization