def write_node_id(nodes: list) -> dict:
    """"
    Writes node IDs and names to 'history_node_id.def' file and returns a dictionary mapping node names to IDs.
    Args:
        nodes (list): List of strings, each containing a node ID and name separated by space and coming from the keyword_reader parser.
        Returns:
            dict: A dictionary where keys are node names and values are node IDs."""
    nodes_file = open('history_node_id_2.def', 'w')
    node_dict = {}
    nodes_file.write('{"OBJECTS":\n[')
    nodes_count = len(nodes)
    for i, node in enumerate(nodes):
        node = node.strip().split(' ')
        node_id = node[0]
        node_name = node[1]
        node_dict[node_name] = node_id

        # Remove comma on last item
        comma = ',' if i < nodes_count - 1 else ''
        nodes_file.write('{"type": "NODE", "name": "'+node_name+'", "id": ['+node_id+']}'+comma+'\n')
    nodes_file.write(']\n}')
    nodes_file.close()
    return node_dict