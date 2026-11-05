import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def _parse_card(line: str) -> str:
    """Read an LS-DYNA card. Stores in a list the field of each card."""
    fields = line.strip().split()
    if not fields:
        raise ValueError("Cannot parse an ID from an empty keyword line.")

    field_1 = line[:10].strip()
    field_2 = line[10:20].strip()
    field_3 = line[20:30].strip()
    field_4 = line[30:40].strip()
    field_5 = line[40:50].strip()
    field_6 = line[50:60].strip()
    field_7 = line[60:70].strip()
    field_8 = line[70:80].strip()
    fields = [field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8]
    if field_1:
        try:
            int(field_1)
        except ValueError:
            pass
        else:
            return fields
    return fields


def _parse_card_id_heading(line: str) -> Tuple[str, str]:
    """Read an ID and heading from fixed-width or whitespace input."""
    match = re.match(r"^\s*(\d+)(?:\s+|(?=[^\d\s]))(.*)$", line)
    if match is None:
        raise ValueError("Cannot parse an ID from an empty history card.")
    element_id = match.group(1)
    element_name = match.group(2).strip()
    if not element_name:
        element_name = "object_" + element_id
    return element_id, element_name


def read_keywords(dir_file: str) -> dict:
    """Reads an LS-DYNA keyword file and returns a dictionary of keywords and their associated cards.
    Args:
        dir_file (str): Path to the LS-DYNA keyword file.
    Returns:
        dict: A dictionary where keys are keywords (without the leading '*') and values are lists of cards associated with each keyword."""

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
        element_id, element_name = _parse_card_id_heading(element)
        element_dict[element_name] = element_id
    return element_dict


def get_dyna_history_beam_id(elements: list) -> dict:
    """Extract beam element names and IDs from history beam-ID cards."""
    return get_dyna_history_node_id(elements)

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
        is_numbered_part = card_suffix.startswith("_") and card_suffix[1:].isdigit()
        is_numbered_contact_part = (
            card.startswith("*PART_CONTACT_")
            and card[len("*PART_CONTACT_") :].isdigit()
        )
        is_averaged_part = (
            card == "*PART_AVERAGED"
            or (
                card.startswith("*PART_AVERAGED_")
                and card[len("*PART_AVERAGED_") :].isdigit()
            )
        )
        if (
            card != "*PART"
            and not is_numbered_part
            and not is_numbered_contact_part
            and not is_averaged_part
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


def get_dyna_part_sections(cards_dict: dict) -> dict:
    """Extract part IDs and beam-section IDs from ``*PART`` cards."""
    parts = {}
    for card, card_lines in cards_dict.items():
        card_suffix = card[len("*PART"):]
        is_numbered_part = card_suffix.startswith("_") and card_suffix[1:].isdigit()
        is_averaged_part = (
            card == "*PART_AVERAGED"
            or (
                card.startswith("*PART_AVERAGED_")
                and card[len("*PART_AVERAGED_") :].isdigit()
            )
        )
        if card != "*PART" and not is_numbered_part and not is_averaged_part:
            continue

        pending_name = None
        for raw_line in card_lines:
            line = raw_line.strip()
            if not line or line.startswith("$"):
                continue
            fields = line.split()
            try:
                part_id = int(fields[0])
            except (IndexError, ValueError):
                pending_name = line
                continue
            if pending_name is None or len(fields) < 2:
                continue
            try:
                section_id = int(fields[1])
            except ValueError:
                section_id = None
            parts[pending_name] = {
                "part_id": part_id,
                "section_id": section_id,
            }
            pending_name = None
    return parts


def get_dyna_beam_section_areas(cards_dict: dict) -> dict:
    """Extract ``section_id -> area`` mappings from beam-section cards."""
    sections = {}
    for card, card_lines in cards_dict.items():
        if not card.startswith("*SECTION_BEAM"):
            continue
        lines = [line.strip() for line in card_lines if line.strip()]
        for index in range(1, len(lines) - 1):
            fields = lines[index].split()
            if len(fields) < 2:
                continue
            try:
                section_id = int(fields[0])
                area = float(lines[index + 1].split()[0])
            except (IndexError, ValueError):
                continue
            sections[section_id] = area
            index += 2
    return sections


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
        #or (
        #  card.startswith("*ELEMENT_SHELL_")
        #   and card[len("*ELEMENT_SHELL_"):].isdigit()
        #)
        if card == "*ELEMENT_SHELL":
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
            joint_id, joint_name = _parse_card_id_heading(lines[0])
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
            motion_id, motion_name = _parse_card_id_heading(lines[0])
            boundary_motions[motion_name] = motion_id
    return boundary_motions

def get_dyna_contact(cards_dict: dict) -> dict:
    """Extract contact object names and IDs from all ``*CONTACT`` cards.

    Contact cards that include an explicit numeric ID and heading use that
    information. For cards without an explicit ID, the one-based contact
    occurrence is used because ``rcforc`` indexes contacts in that order.
    """
    contacts = {}
    contact_index = 0
    for card, card_lines in cards_dict.items():
        if not card.startswith("*CONTACT"):
            continue
        contact_index += 1
        lines = [line for line in card_lines if line.strip()]
        if not lines:
            contact_name = f"contact_{contact_index}"
            contacts[contact_name] = str(contact_index)
            continue
        try:
            contact_id, contact_name = _parse_card_id_heading(lines[0])
        except ValueError:
            contact_id = str(contact_index)
            contact_name = f"contact_{contact_index}"
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
            pretensioner_id = int(_parse_card(lines[0]))
            pretensioner_name = 'pretensioner_' + pretensioner_id.__str__()
            pretensioners[pretensioner_name] = pretensioner_id
        if 'DATABASE_HISTORY_SEATBELT_SLIPRING_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                slipring_id, slipring_name = _parse_card_id_heading(line)
                sliprings[slipring_name] = slipring_id
        if 'DATABASE_HISTORY_SEATBELT_RETRACTOR_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                retractor_id, retractor_name = _parse_card_id_heading(line)
                retractors[retractor_name] = retractor_id
        if 'DATABASE_HISTORY_SEATBELT_ID' in card:
            for line in cards_dict[card]:
                if not line.strip():
                    continue
                seatbelt_id, seatbelt_name = _parse_card_id_heading(line)
                seatbelts[seatbelt_name] = seatbelt_id

    return seatbelts, retractors, sliprings, pretensioners