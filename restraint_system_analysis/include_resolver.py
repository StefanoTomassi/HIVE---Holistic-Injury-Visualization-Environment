"""Resolve the ``*INCLUDE`` tree of an LS-DYNA main keyword file.

LS-DYNA runs are often prepared on a cluster with ``*INCLUDE_PATH`` entries
that do not exist on the post-processing machine. Files are therefore looked
up in this order:

1. the folder of the including file;
2. every ``*INCLUDE_PATH`` / ``*INCLUDE_PATH_RELATIVE`` folder (relative to
   the main keyword folder);
3. a recursive search, by file name, of the user-selected model folders.

``*INCLUDE_TRANSFORM`` ID offsets are accumulated through nested includes so
that every entity can be mapped to the ID written in the binout files.
"""

import os
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Tuple, Union

from restraint_system_analysis.context import IdOffsets, ResolvedInclude

PathLike = Union[str, Path]
_ENCODING = "latin-1"


def _fixed_fields(line: str, width: int = 10, count: int = 8) -> List[str]:
    """Split a fixed-width LS-DYNA card (comma-separated cards are supported)."""
    if "," in line:
        return [field.strip() for field in line.split(",")]
    return [line[i * width:(i + 1) * width].strip() for i in range(count)]


def _to_int(value: str) -> int:
    try:
        return int(float(value)) if value else 0
    except ValueError:
        return 0


def parse_transform_offsets(card_line: str) -> IdOffsets:
    """Parse card 2 of ``*INCLUDE_TRANSFORM`` (IDNOFF ... IDDOFF)."""
    values = [_to_int(field) for field in _fixed_fields(card_line, count=7)]
    values += [0] * (7 - len(values))
    return IdOffsets(*values[:7])


def iter_keyword_blocks(
    path: Path,
    wanted: Optional[Callable[[str], bool]] = None,
) -> Iterator[Tuple[str, List[str]]]:
    """Yield ``(keyword, data_lines)`` for one file, skipping ``$`` comments.

    Args:
        path: Keyword file.
        wanted: Optional predicate on the upper-case keyword. Blocks that are
            not wanted are streamed past without being stored, which keeps
            memory low for large mesh files.
    """
    keyword: Optional[str] = None
    keep = False
    lines: List[str] = []
    with path.open("r", encoding=_ENCODING) as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if line.startswith("*"):
                if keyword is not None and keep:
                    yield keyword, lines
                keyword = line.strip().upper()
                keep = wanted is None or wanted(keyword)
                lines = []
            elif keep and keyword is not None and not line.startswith("$"):
                lines.append(line)
    if keyword is not None and keep:
        yield keyword, lines


def _scan_includes(
    path: Path,
) -> Tuple[List[Tuple[str, IdOffsets]], List[str]]:
    """Return the include entries and include paths declared in one file.

    Only lines starting with ``*INCLUDE`` and their data cards are inspected,
    so large mesh files are streamed without being stored in memory.
    """
    includes: List[Tuple[str, IdOffsets]] = []
    include_paths: List[str] = []
    keyword: Optional[str] = None
    data: List[str] = []

    def flush() -> None:
        if keyword is None:
            return
        cards = [line for line in data if line.strip()]
        if keyword.startswith("*INCLUDE_PATH"):
            include_paths.extend(line.strip() for line in cards)
        elif keyword.startswith("*INCLUDE_TRANSFORM"):
            if cards:
                offsets = (
                    parse_transform_offsets(cards[1]) if len(cards) > 1 else IdOffsets()
                )
                includes.append((cards[0].strip(), offsets))
        elif keyword.startswith("*INCLUDE"):
            # *INCLUDE, *INCLUDE_AUTO_OFFSET, ... : first card is the file name.
            if cards:
                includes.append((cards[0].strip(), IdOffsets()))

    with path.open("r", encoding=_ENCODING) as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if line.startswith("*"):
                flush()
                upper = line.strip().upper()
                keyword = upper if upper.startswith("*INCLUDE") else None
                data = []
            elif keyword is not None and not line.startswith("$"):
                data.append(line)
    flush()
    return includes, include_paths


class _FileIndex:
    """Lazy, case-insensitive file-name index of the model folders."""

    def __init__(self, model_dirs: Sequence[Path]) -> None:
        self._model_dirs = list(model_dirs)
        self._index: Optional[Dict[str, Path]] = None

    def find(self, file_name: str) -> Optional[Path]:
        if self._index is None:
            self._index = {}
            for model_dir in self._model_dirs:
                for root, _dirs, files in os.walk(model_dir):
                    for name in files:
                        self._index.setdefault(name.lower(), Path(root) / name)
        return self._index.get(file_name.lower())


def _normalise(entry: str) -> str:
    return entry.strip().strip('"').replace("\\", "/")


def resolve_includes(
    main_keyword: PathLike,
    model_dirs: Sequence[PathLike] = (),
) -> Tuple[List[ResolvedInclude], List[str]]:
    """Resolve every keyword file reachable from ``main_keyword``.

    Args:
        main_keyword: The keyword file submitted to LS-DYNA.
        model_dirs: Folders searched by file name when a relative path fails.

    Returns:
        ``(files, missing)``: resolved files in include order (main file
        first) and include names that could not be found.
    """
    main_path = Path(main_keyword).resolve()
    base_dir = main_path.parent
    index = _FileIndex([Path(folder) for folder in model_dirs])
    include_dirs: List[Path] = []
    resolved: List[ResolvedInclude] = []
    missing: List[str] = []
    visited = set()

    def locate(entry: str, including_dir: Path) -> Optional[Path]:
        relative = _normalise(entry)
        candidates = [including_dir / relative]
        candidates += [folder / relative for folder in include_dirs]
        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()
        return index.find(Path(relative).name)

    def visit(path: Path, offsets: IdOffsets, depth: int) -> None:
        key = (str(path).lower(), offsets)
        if key in visited:
            return
        visited.add(key)
        resolved.append(ResolvedInclude(path=path, offsets=offsets, depth=depth))
        includes, paths = _scan_includes(path)
        for include_path in paths:
            folder = (base_dir / _normalise(include_path)).resolve()
            if folder not in include_dirs:
                include_dirs.append(folder)
        for entry, include_offsets in includes:
            child = locate(entry, path.parent)
            if child is None:
                missing.append(entry)
                continue
            visit(child, offsets + include_offsets, depth + 1)

    visit(main_path, IdOffsets(), 0)
    return resolved, missing
