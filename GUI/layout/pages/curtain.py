"""Animation curtain composition entry points."""

from GUI.layout.callbacks.plot_callbacks import register_animation_callbacks
from GUI.layout.viewer.viewer_3d import animation_curtain

__all__ = ["animation_curtain", "register_animation_callbacks"]
