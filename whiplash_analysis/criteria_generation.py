from core.dataclasses import simulation_dataclasses as DataClass
import nodes

def main() -> DataClass.DataVisualizationDefinition:
    for node in nodes.keys():
        lateral_view = DataClass.DataVisualizationDefinition(name="Lateral View",
                                                        part_of="Neck",
                                                        type="NODE",
                                                        ID=node,
                                                        y="z_coordinate",
                                                        x="x_coordinate")
        return lateral_view

if __name__ == "__main__":
    main()