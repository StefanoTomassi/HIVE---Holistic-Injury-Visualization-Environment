def read_keywords(dir_file: str) -> dict:
    """Reads an LS-DYNA keyword file and returns a dictionary of keywords and their associated lines.
    Args:
        dir_file (str): Path to the LS-DYNA keyword file.
    Returns:
        dict: A dictionary where keys are keywords (without the leading '*') and values are lists of lines associated with each keyword."""

    file = open(dir_file, 'r')
    cards = {}
    counters = {}
    current_keyword = None
    for line in file:
        line = line.rstrip('\n\r')
        if line.startswith('*'):
            keyword_base = line
            counters[keyword_base] = counters.get(keyword_base, 0) + 1
            current_keyword = f"{keyword_base}_{counters[keyword_base]}"
            cards[current_keyword] = []
            continue
        if line.startswith('$'):
            continue
        if current_keyword is not None:
            cards[current_keyword].append(line)
    file.close()
    return cards

def get_dyna_history_node_id(elements: list) -> dict:
    """
    Extracts node information from a list of lines associated with the 'DATABASE_HISTORY_NODE_ID' keyword.

    Parameters:
    nodes (list): A list of strings, each containing a node ID and name separated by space.

    Returns:
    dict: A dictionary mapping node names to node IDs.
    """
    element_dict = {}
    for i, element in enumerate(elements):
        element = element.strip().split(' ')
        element_id = element[0]
        element_name = element[1]
        element_dict[element_name] = element_id
    return element_dict

def get_dyna_parts(cards_dict: dict) -> dict:
    """
    Extracts the part information from the LS-DYNA keyword cards.

    Parameters:
    cards_dict (dict): A dictionary containing the LS-DYNA keyword cards.

    Returns:
    dict: A dictionary mapping part IDs to part names.
    """
    parts = {}
    for card in cards_dict:
        if '*PART' in card:
            part_id = int(cards_dict[card][1].split()[0].strip())
            part_name = cards_dict[card][0].strip()
            parts[part_name] = part_id
    return parts

def get_dyna_joints(cards_dict: dict) -> dict:
    """
    Extracts the joint information from the LS-DYNA keyword cards.

    Parameters:
    cards_dict (dict): A dictionary containing the LS-DYNA keyword cards.

    Returns:
    dict: A dictionary mapping joint IDs to joint names.
    """
    joints = {}
    for card in cards_dict:
        if '*CONSTRAINED_JOINT' in card and 'STIFFNESS' not in card:
            joint_id = int(cards_dict[card][0].split()[0].strip())
            joint_name = cards_dict[card][0].split()[1].strip()
            joints[joint_name] = joint_id
    return joints

def get_dyna_boundary_motions(cards_dict: dict) -> dict:
    """
    Extracts the boundary motion information from the LS-DYNA keyword cards.

    Parameters:
    cards_dict (dict): A dictionary containing the LS-DYNA keyword cards.

    Returns:
    dict: A dictionary mapping boundary motion IDs to boundary motion names.
    """
    boundary_motions = {}
    for card in cards_dict:
        if 'BOUNDARY_PRESCRIBED_MOTION' in card:
            motion_id = int(cards_dict[card][0].split()[0].strip())
            motion_name = cards_dict[card][0].split()[1].strip()
            boundary_motions[motion_name] = motion_id
    return boundary_motions

def get_dyna_contact(cards_dict: dict) -> dict:
    """
    Extracts the contact information from the LS-DYNA keyword cards.

    Parameters:
    cards_dict (dict): A dictionary containing the LS-DYNA keyword cards.

    Returns:
    dict: A dictionary mapping contact IDs to contact names.
    """
    contacts = {}
    for card in cards_dict:
        if 'CONTACT_AUTOMATIC' in card:
            line_1 = cards_dict[card][0]
            contact_id = int(line_1[:10].split()[0].strip())
            contact_name = line_1[10:30].split()[0].strip()
            contacts[contact_name] = contact_id
    return contacts

def get_selected_part(desired_parts: str, part_dict: dict) -> list:
    part_to_analyze = []
    for key, value in part_dict.items():
        if desired_parts in key:
            part_to_analyze.append(key)
    return part_to_analyze

def get_dyna_seatbelt(cards_dict: dict) -> dict:
    """
    Extracts the seatbelt information from the LS-DYNA keyword cards.

    Parameters:
    cards_dict (dict): A dictionary containing the LS-DYNA keyword cards.

    Returns:
    dict: A dictionary mapping seatbelt IDs to seatbelt names.
    """
    pretensioners = {}
    sliprings = {}
    retractors = {}
    seatbelts = {}
    for card in cards_dict:
        if 'ELEMENT_SEATBELT_PRETENSIONER' in card:
            line_1 = cards_dict[card][0]
            line_2 = cards_dict[card][1]
            pretensioner_id = int(line_1[:10].strip())
            pretensioner_name = 'pretensioner_' + pretensioner_id.__str__()
            pretensioners[pretensioner_name] = pretensioner_id
        if 'DATABASE_HISTORY_SEATBELT_SLIPRING_ID' in card:
            for line in cards_dict[card]:
                slipring_id = int(line[:10].strip())
                slipring_name = line[10:].strip()
                sliprings[slipring_name] = slipring_id
        if 'DATABASE_HISTORY_SEATBELT_RETRACTOR_ID' in card:
            for line in cards_dict[card]:
                retractor_id = int(line[:10].strip())
                retractor_name = line[10:].strip()
                retractors[retractor_name] = retractor_id
        if 'DATABASE_HISTORY_SEATBELT_ID' in card:
            for line in cards_dict[card]:
                seatbelt_id = int(line[:10].strip())
                seatbelt_name = line[10:].strip()
                seatbelts[seatbelt_name] = seatbelt_id

    return seatbelts, retractors, sliprings, pretensioners