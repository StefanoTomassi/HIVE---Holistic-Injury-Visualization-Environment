"""Read the named HBM entities (history nodes, parts, beam sets) of a run.

Names are read from the keyword files, and IDs are shifted by the
``*INCLUDE_TRANSFORM`` offsets so they match the IDs written to binout.
Anatomical part groupings (e.g. one object per rib) are taken from the
Dynasaur ID file shipped with the HBM (VIVA+ ``00_vivaplus_IDs.def``) and
receive the same part offset.
"""

import fnmatch
import json
import re
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

from core.io.keyword_reader import get_dyna_history_node_id, get_dyna_parts
from restraint_system_analysis.context import HbmModel, IdOffsets, ResolvedInclude
from restraint_system_analysis.include_resolver import (
    iter_keyword_blocks,
    resolve_includes,
)

PathLike = Union[str, Path]
DICTIONARY_PATH = Path(__file__).with_name("vivaplus_hbm_dictionary.json")

_WANTED_PREFIXES = (
    "*DATABASE_HISTORY_NODE",
    "*DATABASE_HISTORY_BEAM_SET",
    "*SET_BEAM",
    "*PART",
)


def load_hbm_dictionary(path: PathLike = DICTIONARY_PATH) -> dict:
    """Load the role-to-name dictionary of the HBM."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _wanted(keyword: str) -> bool:
    return keyword.startswith(_WANTED_PREFIXES)


def _ints(line: str) -> List[int]:
    values = []
    for field in re.split(r"[\s,]+", line.strip()):
        if not field:
            continue
        try:
            values.append(int(float(field)))
        except ValueError:
            return []
    return values


def parse_local_history_nodes(lines: Sequence[str]) -> Dict[str, int]:
    """Parse ``*DATABASE_HISTORY_NODE_LOCAL_ID`` cards.

    Card 1 holds ``ID CID REF HFO``; the heading follows on the next card
    (or in columns 41-80 for some writers).
    """
    nodes: Dict[str, int] = {}
    cards = [line for line in lines if line.strip()]
    index = 0
    while index < len(cards):
        card = cards[index]
        node_id = _ints(card[:10])
        if not node_id:
            index += 1
            continue
        heading = card[40:].strip()
        if not heading and index + 1 < len(cards) and not _ints(cards[index + 1][:10]):
            heading = cards[index + 1].strip()
            index += 1
        nodes[heading or f"node_{node_id[0]}"] = node_id[0]
        index += 1
    return nodes


def parse_beam_sets(lines: Sequence[str], titled: bool) -> Tuple[Optional[int], str, List[int]]:
    """Parse one ``*SET_BEAM`` / ``*SET_BEAM_TITLE`` card into (sid, title, ids)."""
    cards = [line for line in lines if line.strip()]
    title = ""
    if titled and cards:
        title = cards.pop(0).strip()
    if not cards:
        return None, title, []
    header = _ints(cards[0][:10])
    set_id = header[0] if header else None
    elements = [value for card in cards[1:] for value in _ints(card) if value > 0]
    return set_id, title, elements


def _history_beam_set_ids(lines: Sequence[str]) -> List[int]:
    return [value for line in lines for value in _ints(line) if value > 0]


def _hbm_offsets(files: Sequence[ResolvedInclude], pattern: str) -> IdOffsets:
    for resolved in files:
        if fnmatch.fnmatch(resolved.path.name.lower(), pattern.lower()):
            return resolved.offsets
    return IdOffsets()


def _load_def_json(path: Path) -> object:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Some hand-edited .def files contain trailing commas.
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", text))


def read_part_groups(def_path: Path, part_offset: int) -> Dict[str, List[int]]:
    """Read ``OBJECT`` part groupings from a Dynasaur ID file and offset them."""
    data = _load_def_json(def_path)
    blocks = data if isinstance(data, list) else [data]
    groups: Dict[str, List[int]] = {}
    for block in blocks:
        if not isinstance(block, dict):
            continue
        for item in block.get("OBJECTS", []):
            if item.get("type") != "OBJECT" or "id" not in item:
                continue
            groups[item["name"]] = [int(pid) + part_offset for pid in item["id"]]
    return groups


def _find_file(name: str, folders: Sequence[Path]) -> Optional[Path]:
    for folder in folders:
        for candidate in folder.rglob(name):
            if candidate.is_file():
                return candidate
    return None


def read_hbm_model(
    main_keyword: PathLike,
    model_dirs: Sequence[PathLike],
    dictionary: Optional[Mapping[str, object]] = None,
) -> HbmModel:
    """Resolve the include tree and collect the named HBM entities.

    Args:
        main_keyword: Main ``.key`` file of the run.
        model_dirs: Folders searched for include files and the HBM ID file.
        dictionary: HBM role dictionary; defaults to the VIVA+ dictionary.

    Returns:
        An :class:`HbmModel` with offset IDs.
    """
    dictionary = dictionary or load_hbm_dictionary()
    folders = [Path(folder) for folder in model_dirs]
    files, missing = resolve_includes(main_keyword, folders)
    model = HbmModel(files=files, missing_includes=missing)
    model.offsets = _hbm_offsets(files, str(dictionary.get("hbm_main_file_glob", "*")))

    set_titles: Dict[int, Tuple[str, List[int]]] = {}
    history_beam_sets: List[int] = []
    for resolved in files:
        offsets = resolved.offsets
        for keyword, lines in iter_keyword_blocks(resolved.path, _wanted):
            if keyword.startswith("*DATABASE_HISTORY_NODE_LOCAL"):
                for name, node_id in parse_local_history_nodes(lines).items():
                    model.nodes[name] = node_id + offsets.node
            elif keyword.startswith("*DATABASE_HISTORY_NODE_ID"):
                cards = [line for line in lines if line.strip()]
                for name, node_id in get_dyna_history_node_id(cards).items():
                    model.nodes[name] = int(node_id) + offsets.node
            elif keyword.startswith("*DATABASE_HISTORY_BEAM_SET"):
                history_beam_sets += [
                    set_id + offsets.set for set_id in _history_beam_set_ids(lines)
                ]
            elif keyword.startswith("*SET_BEAM"):
                set_id, title, elements = parse_beam_sets(
                    lines, titled=keyword.endswith("_TITLE")
                )
                if set_id is not None:
                    set_titles[set_id + offsets.set] = (
                        title or f"beam_set_{set_id}",
                        [element + offsets.element for element in elements],
                    )
            elif keyword == "*PART" or keyword.startswith("*PART_"):
                for name, part_id in get_dyna_parts({"*PART": lines}).items():
                    model.parts[name] = int(part_id) + offsets.part

    for set_id in history_beam_sets:
        if set_id in set_titles:
            title, elements = set_titles[set_id]
            model.beam_sets[title] = elements

    ids_def_name = str(dictionary.get("dynasaur_ids_def", ""))
    ids_def = _find_file(ids_def_name, folders) if ids_def_name else None
    if ids_def is not None:
        known_parts = set(model.parts.values())
        for name, part_ids in read_part_groups(ids_def, model.offsets.part).items():
            present = [pid for pid in part_ids if pid in known_parts]
            if present:
                model.part_groups[name] = present
    return model
