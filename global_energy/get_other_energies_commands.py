from core.dataclasses import simulation_dataclasses
from core.io.create_criteria import create_data_visualization
def get_other_energies_commands(boundaries, joints, contacts):
    
    other_energies_data_visualization = []
    for boundary in boundaries:
        BoundaryConditionEnergy = simulation_dataclasses.DataVisualizationDefinition(name="Boundary Condition Energy",
                                                        part_of= "boundary" + boundary,
                                                        type="BOUNDARY_CONDITION",
                                                        ID=boundary,
                                                        y="energy",
                                                        x="time")
        other_energies_data_visualization.append(BoundaryConditionEnergy)
    for joint in joints:
        JointForceEnergy = simulation_dataclasses.DataVisualizationDefinition(name=f"Joint Energy - {joint}",
                                                        part_of= "joint" + joint,
                                                        type="JOINT",
                                                        ID= joint,
                                                        y="energy",
                                                        x="time")
        other_energies_data_visualization.append(JointForceEnergy)
    for contact in contacts:
        FrictionContactEnergy = simulation_dataclasses.DataVisualizationDefinition(name=f"Friction contact Energy - {contact}",
                                                        part_of= "friction energy of " + contact,
                                                        type="SLEOUT",
                                                        ID= contact,
                                                        y="friction_energy",
                                                        x="time")
        other_energies_data_visualization.append(FrictionContactEnergy)
    TotalFrictionContactEnergy = simulation_dataclasses.DataVisualizationDefinition(name=f"Total contact energy",
                                                    part_of= "total friction energy",
                                                    type="SLEOUT",
                                                    ID= contact,
                                                    y="total_friction",
                                                    x="time")
    other_energies_data_visualization.append(TotalFrictionContactEnergy)
    TotalContactEnergy = simulation_dataclasses.DataVisualizationDefinition(name=f"Total contact energy",
                                                    part_of= "total contact energy",
                                                    type="SLEOUT",
                                                    ID= contact,
                                                    y="total_energy",
                                                    x="time")
    other_energies_data_visualization.append(TotalContactEnergy)  

    other_energy_data_visualization = []
    for energy in other_energies_data_visualization:
        create_data_visualization(items = other_energy_data_visualization,
                                  name = energy.name,
                                  part_of = energy.part_of,
                                  ID = energy.ID,
                                  crit_type = energy.type,
                                  x_crit = energy.x,
                                  y_crit = energy.y)
     
    return  other_energies_data_visualization, other_energy_data_visualization
