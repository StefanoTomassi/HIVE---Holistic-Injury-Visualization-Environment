from core.dataclasses import simulation_dataclasses
from core.io.create_criteria import create_data_visualization

def get_other_energies_commands():

    BoundaryConditionEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Boundary Condition Energy",
                                                        part_of="Other Energies",
                                                        type="BOUNDARY_CONDITION",
                                                        ID="Model",
                                                        y="energy",
                                                        x="time")
    JointForceEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Joint Force Energy",
                                                        part_of="Other Energies",
                                                        type="JOINT",
                                                        ID="Model",
                                                        y="energy",
                                                        x="time")
    FrictionContactEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Friction contact Energy",
                                                        part_of="Other Energies",
                                                        type="SLEOUT",
                                                        ID="Model",
                                                        y="energy",
                                                        x="time")
    TotalContactEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Total contact energy",
                                                        part_of="Other Energies",
                                                        type="SLEOUT",
                                                        ID="Model",
                                                        y="energy",
                                                        x="time")

    other_energies_data_visualization = [BoundaryConditionEnergy, JointForceEnergy, FrictionContactEnergy, TotalContactEnergy]
    energy_data_visualization = []
    for energy in other_energies_data_visualization:
        create_data_visualization(items = energy_data_visualization,
                                  name = energy.name,
                                  part_of = energy.part_of,
                                  ID = energy.ID,
                                  crit_type = energy.type,
                                  x_crit = energy.x,
                                  y_crit = energy.y)
     
    return  other_energies_data_visualization, energy_data_visualization


def get_other_energies_definitions():
    #fai una simulazione in cui metti un joint, un contatto e un boundary condition esterno. 
    return 0