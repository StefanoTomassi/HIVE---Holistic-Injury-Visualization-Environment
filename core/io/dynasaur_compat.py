"""Compatibility helpers for Dynasaur versions used by HIVE."""

from functools import wraps
from typing import Any, Callable

import numpy as np


def enable_rcforc_resultant_force() -> None:
    """Make ``RCForc`` expose a derived ``resultant_force`` channel.

    Some Dynasaur releases document ``resultant_force`` as an allowed RCForc
    channel but only load channels physically stored in the binout. LS-DYNA
    files may instead contain only the Cartesian force components.
    """
    from dynasaur.data.ls_dyna import RCForc

    if getattr(RCForc, "_hive_resultant_force_enabled", False):
        return

    original_read_data_channels: Callable[..., Any] = RCForc._read_data_channels

    @wraps(original_read_data_channels)
    def read_data_channels_with_resultant_force(self: Any, *args: Any, **kwargs: Any) -> None:
        original_read_data_channels(self, *args, **kwargs)
        if "resultant_force" in self._data:
            return

        component_names = ("x_force", "y_force", "z_force")
        if not all(name in self._data for name in component_names):
            return

        self._data["resultant_force"] = np.sqrt(
            self._data["x_force"] ** 2
            + self._data["y_force"] ** 2
            + self._data["z_force"] ** 2
        )

    RCForc._read_data_channels = read_data_channels_with_resultant_force
    RCForc._hive_resultant_force_enabled = True
