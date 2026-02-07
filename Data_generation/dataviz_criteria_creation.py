def create_dataviz_criteria(nodes: dict):

    criteria = open('dataviz_criteria_2.def', 'w')
    criteria.write('[\n\t{"UNIT":{ "time": "ms", "length": "mm", "mass": "kg"}},\n')
    criteria.write('{"DATA VISUALIZATION":[\n')
    nodes_count = len(nodes)
    for i, node in enumerate(nodes):
        comma = ',' if i < nodes_count - 1 else ''
        criteria.write('{"name": "xvel","part_of": "'+node+'",\n')
        criteria.write(' "y": {"type": "NODE", "ID": "'+node+'", "array": ["(0, x_velocity)"]},\n')
        criteria.write(' "x": {"type": "NODE", "ID": "'+node+'", "array": ["(0, time)"]}}'+comma+'\n')
    criteria.write(']}]')
    criteria.close()

    