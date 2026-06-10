from core.dataclasses import simulation_dataclasses
from core.io.create_criteria import create_data_visualization

def get_global_commands():

    EnergyRatio = simulation_dataclasses.DataVisualizationDefinition(name="Energy Ratio", 
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="energy_ratio",
                                                        x="time")

    TotalEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Total Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="total_energy",
                                                        x="time")
    InternalEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Internal Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="internal_energy",
                                                        x="time")
    KineticEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Kinetic Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="kinetic_energy",
                                                        x="time")
    SpringAndDampingEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Spring and Damping Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="spring_and_damper_energy",
                                                        x="time")
    ExternalWork = simulation_dataclasses.DataVisualizationDefinition(name="External Work",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="external_work",
                                                        x="time")
    SystemDampingEnergy = simulation_dataclasses.DataVisualizationDefinition(name="System Damping Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="system_damping_energy",
                                                        x="time")
    HourglassEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Hourglass Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="hourglass_energy",
                                                        x="time")
    SlidingInterfaceEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Sliding Interface Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="sliding_interface_energy",
                                                        x="time")
    JointInternalEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Joint Internal Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="joint_internal_energy",
                                                        x="time")
    AddedMass = simulation_dataclasses.DataVisualizationDefinition(name="Added Mass",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="added_mass",
                                                        x="time")
    ErodedHourglassEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Eroded Hourglass Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="eroded_hourglass_energy",
                                                        x="time")
    ErodedKineticEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Eroded Kinetic Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="eroded_kinetic_energy",
                                                        x="time")
    ErodedInternalEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Eroded Internal Energy",
                                                        part_of="Global Energy",
                                                        type="ENERGY_GLOBAL",
                                                        ID="Model",
                                                        y="eroded_internal_energy",
                                                        x="time")
    
    global_energies = [EnergyRatio, TotalEnergy, InternalEnergy, KineticEnergy, SpringAndDampingEnergy, ExternalWork, SystemDampingEnergy, HourglassEnergy, SlidingInterfaceEnergy, JointInternalEnergy, AddedMass, ErodedHourglassEnergy, ErodedKineticEnergy, ErodedInternalEnergy]
    
    energy_data_visualization = []
    for energy in global_energies:
        create_data_visualization(items = energy_data_visualization,
                                  name = energy.name,
                                  part_of = energy.part_of,
                                  ID = energy.ID,
                                  crit_type = energy.type,
                                  x_crit = energy.x,
                                  y_crit = energy.y)
     
    return global_energies, energy_data_visualization
    