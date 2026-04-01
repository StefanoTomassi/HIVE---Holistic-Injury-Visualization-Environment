def create_dataviz_criteria(nodes: dict, x_crit: str, y_crit: str):

    criteria = open('dataviz_' + x_crit + '_' + y_crit + '.def', 'w')
    criteria.write('[\n\t{"UNIT":{ "time": "ms", "length": "mm", "mass": "kg"}},\n')
    criteria.write('{"DATA VISUALIZATION":[\n')
    nodes_count = len(nodes)
    for i, node in enumerate(nodes):
        comma = ',' if i < nodes_count - 1 else ''
        criteria.write('{"name": "lateral","part_of": "'+node+'",\n')
        criteria.write(' "y": {"type": "NODE", "ID": "'+node+'", "array": ["(0, '+y_crit+')"]},\n')
        criteria.write(' "x": {"type": "NODE", "ID": "'+node+'", "array": ["(0, '+x_crit+')"]}}'+comma+'\n')
    criteria.write(']}]')
    criteria.close()

    