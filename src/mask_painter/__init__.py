"""
Mask Painter - Planaria Particle Simulator

A modular PyQt5 application for simulating particle movement and exposure
in planaria-shaped regions with configurable dividers and catching mechanisms.

Main Components:
- ConfigManager: Configuration and profile management
- ParticleManager: Particle physics and lifecycle
- ParticleSpawner: Timed particle spawning
- DividerManager: Region-based dividers and catching
- MaskSystem: Grid-based exposure tracking
- VisualizationManager: PyQtGraph visualization
- UI Components: Reusable parameter controls
- MaskPainter: Main application orchestrator
"""

from .mask_painter import MaskPainter, main
from .config_manager import ConfigManager
from .particle import Particle, ParticleManager
from .spawner import ParticleSpawner
from .divider import Divider, DividerManager
from .mask_system import MaskSystem
from .visualization import VisualizationManager
from .ui_components import (
    ParameterSlider, ColorButton, DividerControlPanel,
    SpawnerControlPanel, StepControlPanel
)

__version__ = "2.0.0"
__author__ = "Mask Painter Development Team"

__all__ = [
    'MaskPainter', 'main',
    'ConfigManager',
    'Particle', 'ParticleManager',
    'ParticleSpawner',
    'Divider', 'DividerManager',
    'MaskSystem',
    'VisualizationManager',
    'ParameterSlider', 'ColorButton', 'DividerControlPanel',
    'SpawnerControlPanel', 'StepControlPanel'
]
