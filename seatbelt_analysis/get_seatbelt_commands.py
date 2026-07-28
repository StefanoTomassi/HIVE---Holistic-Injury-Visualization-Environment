from core.dataclasses import simulation_dataclasses
from core.io.create_criteria import create_data_visualization

def get_seatbelt_commands(rings, retractors, belt_segments):

    seatbelt_data_visualization = []
    for belt in belt_segments:
        BeltLength = simulation_dataclasses.DataVisualizationDefinition(name="belt_length", 
                                                            part_of=belt,
                                                            type="SEAT_BELT",
                                                            ID=belt,
                                                            y="belt_length",
                                                            x="time")
        BeltForce = simulation_dataclasses.DataVisualizationDefinition(name="belt_force",
                                                            part_of= belt,
                                                            type="SEAT_BELT",
                                                            ID=belt,
                                                            y="belt_force",
                                                            x="time")
        seatbelt_data_visualization.append(BeltLength)
        seatbelt_data_visualization.append(BeltForce)
    for ring in rings:
        RingSlip = simulation_dataclasses.DataVisualizationDefinition(name="ring_slip",
                                                            part_of=ring,
                                                            type="SLIP_RING",
                                                            ID=ring,
                                                            y="ring_slip",
                                                            x="time")
        seatbelt_data_visualization.append(RingSlip)
    for retractor in retractors:
        RetractorPullOut = simulation_dataclasses.DataVisualizationDefinition(name="pull_out",
                                                            part_of=retractor,
                                                            type="RETRACTOR",
                                                            ID=retractor,
                                                            y="retractor_pull_out",
                                                            x="time")
        RetractorForce = simulation_dataclasses.DataVisualizationDefinition(name="force",
                                                            part_of=retractor,
                                                            type="RETRACTOR",
                                                            ID=retractor,
                                                            y="retractor_force",
                                                            x="time")
        seatbelt_data_visualization.append(RetractorPullOut)
        seatbelt_data_visualization.append(RetractorForce)
    seatbelt_data_visualizations_definitions = []
    for data in seatbelt_data_visualization:
        create_data_visualization(items = seatbelt_data_visualizations_definitions,
                                  name = data.name,
                                  part_of = data.part_of,
                                  ID = data.ID,
                                  crit_type = data.type,
                                  x_crit = data.x,
                                  y_crit = data.y)
    return seatbelt_data_visualization, seatbelt_data_visualizations_definitions