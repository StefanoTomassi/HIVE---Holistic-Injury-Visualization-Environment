from dataclasses import dataclass, field
from pathlib import Path
@dataclass
class SimulationData:
    module_type: str #Whiplash, global energy, ...
    name: str #Rotated_head_neck, impact_added_mass,...
    output_dir: Path #directory where the LS-DYNA output files are stored
    criteria: list = field(default_factory=list) #serve davvero storarlo all'interno della classe se poi non lo riuso?? Altrimenti non ha seno storarlo

@dataclass
class PlotStyle:
    font_family: str
    font_sans_serif: str
    font_size: float
    axes_spines_top: bool
    axes_spines_right: bool
    axes_linewidth: float
    xtick_major_size: float
    ytick_major_size: float
    xtick_major_width: float
    ytick_major_width: float
    xtick_direction: str
    ytick_direction: str
    pdf_fonttype: float
    ps_fonttype: float
    svg_fonttype: str
    savefig_dpi: int  

@dataclass
class AnimationStyle:
    component_list: list
    
@dataclass
class DataVisualizationDefinition:
    name: str
    part_of: str
    type: str
    ID: str
    y: str
    x: str

@dataclass
class CriteriaDefinition:
    name: str
    part_of: str
    type: str
    ID: str
    criterion: str