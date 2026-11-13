"""Shared inputs and configuration for restraint-system analyses."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class SimulationFiles:
    """Paths belonging to one LS-DYNA simulation.

    Attributes:
        simulation_dir: Run folder containing the ``binout*`` files.
        main_keyword: Main ``.key`` file that was submitted to LS-DYNA.
        model_dirs: Folders searched for ``*INCLUDE`` files whose relative
            paths do not resolve on this machine (e.g. VIVA+ and the cockpit).
        output_dir: Folder for the generated ``.def`` and ``.csv`` files.
    """

    simulation_dir: Path
    main_keyword: Optional[Path] = None
    model_dirs: Tuple[Path, ...] = field(default_factory=tuple)
    keyword_files: Tuple[Path, ...] = field(default_factory=tuple)
    binout_files: Tuple[Path, ...] = field(default_factory=tuple)
    d3plot_files: Tuple[Path, ...] = field(default_factory=tuple)
    output_dir: Optional[Path] = None

    @property
    def data_source(self) -> str:
        """Glob pattern used by Dynasaur to read the binout files."""
        return str(self.simulation_dir / "binout*")

    @property
    def resolved_output_dir(self) -> Path:
        """Output folder, defaulting to ``<run>/hive_restraint``."""
        return self.output_dir or (self.simulation_dir / "hive_restraint")


@dataclass(frozen=True)
class AnalysisPlan:
    """Select the analysis areas to run for one simulation."""

    seatbelt: bool = False
    airbag: bool = False
    hbm: bool = True
    vehicle_parts: bool = False


@dataclass(frozen=True)
class IdOffsets:
    """ID offsets applied by ``*INCLUDE_TRANSFORM`` (accumulated when nested)."""

    node: int = 0
    element: int = 0
    part: int = 0
    material: int = 0
    set: int = 0
    function: int = 0
    define: int = 0

    def __add__(self, other: "IdOffsets") -> "IdOffsets":
        return IdOffsets(
            node=self.node + other.node,
            element=self.element + other.element,
            part=self.part + other.part,
            material=self.material + other.material,
            set=self.set + other.set,
            function=self.function + other.function,
            define=self.define + other.define,
        )


@dataclass(frozen=True)
class ResolvedInclude:
    """One keyword file of the model, with the offsets that apply to it."""

    path: Path
    offsets: IdOffsets
    depth: int


@dataclass
class HbmModel:
    """Named HBM entities with their IDs as seen in this run's binout.

    All IDs already include the ``*INCLUDE_TRANSFORM`` offsets.
    """

    nodes: Dict[str, int] = field(default_factory=dict)
    parts: Dict[str, int] = field(default_factory=dict)
    part_groups: Dict[str, List[int]] = field(default_factory=dict)
    beam_sets: Dict[str, List[int]] = field(default_factory=dict)
    offsets: IdOffsets = field(default_factory=IdOffsets)
    files: List[ResolvedInclude] = field(default_factory=list)
    missing_includes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CriterionStatus:
    """Whether a criterion could be evaluated with this run's outputs."""

    name: str
    region: str
    available: bool
    missing_reason: str = ""
