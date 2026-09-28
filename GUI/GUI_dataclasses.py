@dataclass
class GenericDropDown:
    """Defines a generic dropdown menu for the GUI."""

    name: str
    options: List[str]
    default: str

