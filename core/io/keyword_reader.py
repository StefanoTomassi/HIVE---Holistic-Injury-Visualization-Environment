import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def _parse_fixed_width_id(line: str) -> str:
    """Read an LS-DYNA ID from columns 1-10, with whitespace fallback."""
    fields = line.strip().split()
    if not fields:
        raise ValueError("Cannot parse an ID from an empty keyword line.")

    fixed_width_id = line[:10].strip()
    if fixed_width_id:
        try:
            int(fixed_width_id)
        except ValueError:
            pass
        else:
            return fixed_width_id
    return fields[0]


def _parse_fixed_width_id_name(line: str) -> Tuple[str, str]:
    """Read an ID and name from a fixed-width LS-DYNA record."""
    element_id = _parse_fixed_width_id(line)
    element_name = line[10:].strip()
    fields = line.strip().split()
    if not element_name and len(fields) > 1:
        element_name = fields[1]
    if not element_name:
        element_name = "object_" + element_id
    return element_id, element_name


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
    for element in elements:
        if not element.strip():
            continue

        element_id, element_name = _parse_fixed_width_id_name(element)
        element_dict[element_name] = element_id
    return element_dict

def get_dyna_parts(cards_dict: dict) -> dict:
    """
    Extract part names and IDs from LS-DYNA ``*PART`` cards.

    Parameters:
    cards_dict (dict): Keyword cards returned by :func:`read_keywords`.

    Returns:
    dict: A dictionary mapping part names to part IDs.

    Both common LS-DYNA layouts are supported:

    * one ``*PART`` card per part, with the name followed by its data line;
    * one consolidated ``*PART`` card containing repeated name/data pairs,
      optionally preceded by ``$HWCOLOR COMPS`` and ``$NAME`` comments.

    ``read_keywords`` removes comment lines, so the parser deliberately uses
    the sequence of a non-numeric name line followed by a numeric PID line
    instead of relying on a fixed number of lines per part.
    """
    parts = {}
    for card, card_lines in cards_dict.items():
        card_suffix = card[len("*PART"):]
        if card != "*PART" and not (
            card_suffix.startswith("_") and card_suffix[1:].isdigit()
        ):
            continue

        pending_name = None
        for raw_line in card_lines:
            line = raw_line.strip()
            if not line or line.startswith("$"):
                continue

            fields = line.split()
            first_field = fields[0]
            try:
                part_id = int(first_field)
            except ValueError:
                pending_name = line
                continue

            if pending_name is None:
                continue
            parts[pending_name] = part_id
            pending_name = None
    return parts


def get_elements(
    cards_dict: dict,
    pickle_path: Optional[Union[Path, str]] = "element_connectivity.pkl",
) -> Tuple[Dict[int, Tuple[int, ...]], Dict[int, Tuple[int, ...]]]:
    """Read shell and solid element node connectivity.

    Parameters:
        cards_dict: Keyword cards returned by :func:`read_keywords`.
        pickle_path: Path where the two connectivity dictionaries are
            serialized. It defaults to ``element_connectivity.pkl`` in the
            current working directory. Pass ``None`` to disable serialization.

    Returns:
        A tuple ``(shell_elements, solid_elements)``. Both dictionaries map
        ``element_id`` to a tuple of node IDs. Shell tuples contain four node
        IDs; solid tuples contain eight node IDs.

    ``*ELEMENT_SHELL`` records contain the element and part IDs on one line.
    ``*ELEMENT_SOLID`` records may contain all fields on one line or may use
    the LS-DYNA two-line form, with element/part IDs on the first line and
    node IDs on the following line.
    """
    shell_elements: Dict[int, Tuple[int, ...]] = {}
    solid_elements: Dict[int, Tuple[int, ...]] = {}
    shell_parts: Dict[int, int] = {}
    solid_parts: Dict[int, int] = {}

    def nonempty_lines(lines: List[str]) -> List[str]:
        return [line.strip() for line in lines if line.strip()]

    def parse_element_part(line: str) -> Tuple[int, int]:
        fields = line.split()
        if len(fields) < 2:
            raise ValueError(f"Invalid element record: {line!r}")
        return int(fields[0]), int(fields[1])

    for card, card_lines in cards_dict.items():
        if card == "*ELEMENT_SHELL" or (
            card.startswith("*ELEMENT_SHELL_")
            and card[len("*ELEMENT_SHELL_"):].isdigit()
        ):
            lines = nonempty_lines(card_lines)
            index = 0
            while index < len(lines):
                fields = lines[index].split()
                if len(fields) < 6:
                    raise ValueError(f"Invalid shell element record: {lines[index]!r}")
                element_id, _ = parse_element_part(lines[index])
                _, part_id = parse_element_part(lines[index])
                shell_elements[element_id] = tuple(
                    int(node_id) for node_id in fields[2:6]
                )
                shell_parts[element_id] = part_id
                index += 1
            continue

        if card == "*ELEMENT_SOLID" or (
            card.startswith("*ELEMENT_SOLID_")
            and card[len("*ELEMENT_SOLID_"):].isdigit()
        ):
            lines = nonempty_lines(card_lines)
            index = 0
            while index < len(lines):
                fields = lines[index].split()
                if len(fields) < 2:
                    raise ValueError(
                        f"Invalid solid element record: {lines[index]!r}"
                    )
                element_id, _ = parse_element_part(lines[index])
                _, part_id = parse_element_part(lines[index])
                node_fields = fields[2:]
                index += 1

                if len(node_fields) < 8:
                    if index >= len(lines):
                        raise ValueError(
                            f"Missing node record for solid element {element_id}."
                        )
                    node_fields = lines[index].split()
                    index += 1
                if len(node_fields) < 8:
                    raise ValueError(
                        f"Invalid node record for solid element {element_id}: "
                        f"{node_fields!r}"
                    )
                solid_elements[element_id] = tuple(
                    int(node_id) for node_id in node_fields[:8]
                )
                solid_parts[element_id] = part_id

    if pickle_path is not None:
        output_path = Path(pickle_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as stream:
            pickle.dump(
                {
                    "shell_elements": shell_elements,
                    "solid_elements": solid_elements,
                    "shell_parts": shell_parts,
                    "solid_parts": solid_parts,
                },
                stream,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

    return shell_elements, solid_elements

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
            lines = [line for line in cards_dict[card] if line.strip()]
            if not lines:
                continue
            joint_id, joint_name = _parse_fixed_width_id_name(lines[0])
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
            lines = [line for line in cards_dict[card] if line.strip()]
            if not lines:
                continue
            motion_id, motion_name = _parse_fixed_width_id_name(lines[0])
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
            lines = [line for line in cards_dict[card] if line.strip()]
            if not lines:
                continue
            contact_id, contact_name = _parse_fixed_width_id_name(lines[0])
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
            lines = [line for line in cards_dict[card] if line.strip()]
            if not lines:
                continue
            pretensioner_id = int(_parse_fixed_width_id(lines[0]))
            pretensioner_name = 'pretensioner_' + pretensioner_id.__str__()
            pretensioners[pretensioner_name] = pretensioner_id
        if 'DATABASE_HISTORY_SEATBELT_SLIPRING_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                slipring_id, slipring_name = _parse_fixed_width_id_name(line)
                sliprings[slipring_name] = slipring_id
        if 'DATABASE_HISTORY_SEATBELT_RETRACTOR_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                retractor_id, retractor_name = _parse_fixed_width_id_name(line)
                retractors[retractor_name] = retractor_id
        if 'DATABASE_HISTORY_SEATBELT_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                seatbelt_id, seatbelt_name = _parse_fixed_width_id_name(line)
                seatbelts[seatbelt_name] = seatbelt_id

    return seatbelts, retractors, sliprings, pretensioners