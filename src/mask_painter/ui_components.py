"""
Reusable UI components for the mask painter application.
Provides custom widgets for parameter control and divider management.
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Dict, Any, List, Callable, Optional


class ParameterSlider(QtWidgets.QWidget):
    """Reusable slider with label for parameter control"""
    
    valueChanged = QtCore.pyqtSignal(float)  # Emits actual value (not slider position)
    
    def __init__(self, label: str, min_val: float, max_val: float, 
                 initial_val: float = None, decimals: int = 2, 
                 slider_range: int = 1000, parent=None):
        """
        Initialize parameter slider.
        
        Args:
            label: Display label for the parameter
            min_val: Minimum value
            max_val: Maximum value
            initial_val: Initial value (uses min_val if None)
            decimals: Number of decimal places to display
            slider_range: Internal slider range (for precision)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.min_val = min_val
        self.max_val = max_val
        self.decimals = decimals
        self.slider_range = slider_range
        
        if initial_val is None:
            initial_val = min_val
        
        self.setup_ui(label, initial_val)
    
    def setup_ui(self, label: str, initial_val: float):
        """Setup the UI components"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QtWidgets.QLabel(label)
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, self.slider_range)
        self.slider.setValue(self._value_to_slider(initial_val))
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
        
        # Value display
        self.value_label = QtWidgets.QLabel()
        self.value_label.setMinimumWidth(60)
        self.value_label.setAlignment(QtCore.Qt.AlignRight)
        self._update_value_label(initial_val)
        layout.addWidget(self.value_label)
    
    def _value_to_slider(self, value: float) -> int:
        """Convert actual value to slider position"""
        normalized = (value - self.min_val) / (self.max_val - self.min_val)
        return int(normalized * self.slider_range)
    
    def _slider_to_value(self, slider_pos: int) -> float:
        """Convert slider position to actual value"""
        normalized = slider_pos / self.slider_range
        return self.min_val + normalized * (self.max_val - self.min_val)
    
    def _on_slider_changed(self, slider_pos: int):
        """Handle slider value change"""
        value = self._slider_to_value(slider_pos)
        self._update_value_label(value)
        self.valueChanged.emit(value)
    
    def _update_value_label(self, value: float):
        """Update the value display label"""
        self.value_label.setText(f"{value:.{self.decimals}f}")
    
    def set_value(self, value: float):
        """Set the slider value programmatically"""
        value = max(self.min_val, min(self.max_val, value))
        self.slider.setValue(self._value_to_slider(value))
    
    def get_value(self) -> float:
        """Get the current value"""
        return self._slider_to_value(self.slider.value())
    
    def set_range(self, min_val: float, max_val: float):
        """Update the value range"""
        current_val = self.get_value()
        self.min_val = min_val
        self.max_val = max_val
        
        # Clamp current value to new range
        new_val = max(min_val, min(max_val, current_val))
        self.set_value(new_val)


class ColorButton(QtWidgets.QPushButton):
    """Color picker button"""
    
    colorChanged = QtCore.pyqtSignal(str)  # Emits hex color string
    
    def __init__(self, initial_color: str = '#FF5722', parent=None):
        """
        Initialize color button.
        
        Args:
            initial_color: Initial color as hex string
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_color = initial_color
        self.setText("Color")
        self.setMaximumWidth(60)
        self.update_button_color()
        
        self.clicked.connect(self.pick_color)
    
    def update_button_color(self):
        """Update button background color"""
        self.setStyleSheet(f"QPushButton {{ background-color: {self.current_color}; }}")
    
    def pick_color(self):
        """Open color picker dialog"""
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(self.current_color), 
            self, 
            "Select Color"
        )
        
        if color.isValid():
            self.current_color = color.name()
            self.update_button_color()
            self.colorChanged.emit(self.current_color)
    
    def set_color(self, color: str):
        """Set color programmatically"""
        self.current_color = color
        self.update_button_color()
    
    def get_color(self) -> str:
        """Get current color as hex string"""
        return self.current_color


class DividerControlPanel(QtWidgets.QWidget):
    """Complete divider management UI"""
    
    dividerChanged = QtCore.pyqtSignal()  # Emitted when any divider property changes
    dividerSelected = QtCore.pyqtSignal(str)  # Emitted when divider selection changes
    
    def __init__(self, parent=None):
        """Initialize divider control panel"""
        super().__init__(parent)
        
        self.dividers = []
        self.current_divider_name = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Divider selection
        selection_layout = QtWidgets.QHBoxLayout()
        
        selection_layout.addWidget(QtWidgets.QLabel("Divider:"))
        
        self.divider_combo = QtWidgets.QComboBox()
        self.divider_combo.currentTextChanged.connect(self.on_divider_selected)
        selection_layout.addWidget(self.divider_combo)
        
        self.new_button = QtWidgets.QPushButton("New")
        self.new_button.clicked.connect(self.create_new_divider)
        selection_layout.addWidget(self.new_button)
        
        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_current_divider)
        selection_layout.addWidget(self.remove_button)
        
        layout.addLayout(selection_layout)
        
        # Divider properties
        self.position_slider = ParameterSlider("Position:", 0, 300, 150, decimals=1)
        self.position_slider.valueChanged.connect(self.on_position_changed)
        layout.addWidget(self.position_slider)
        
        self.probability_slider = ParameterSlider("Probability:", 0, 1, 0.1, decimals=3)
        self.probability_slider.valueChanged.connect(self.on_probability_changed)
        layout.addWidget(self.probability_slider)
        
        # Color selection
        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(QtWidgets.QLabel("Color:"))
        
        self.color_button = ColorButton()
        self.color_button.colorChanged.connect(self.on_color_changed)
        color_layout.addWidget(self.color_button)
        
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Enable/disable controls initially
        self.update_controls_state()
    
    def set_dividers(self, dividers: List[Dict[str, Any]]):
        """Update the divider list"""
        self.dividers = dividers
        self.update_divider_combo()
        self.update_controls_state()
    
    def update_divider_combo(self):
        """Update the divider combo box"""
        self.divider_combo.blockSignals(True)
        self.divider_combo.clear()
        
        for divider in self.dividers:
            self.divider_combo.addItem(divider['name'])
        
        # Select current divider if it still exists
        if self.current_divider_name:
            index = self.divider_combo.findText(self.current_divider_name)
            if index >= 0:
                self.divider_combo.setCurrentIndex(index)
            else:
                self.current_divider_name = None
        
        self.divider_combo.blockSignals(False)
    
    def update_controls_state(self):
        """Enable/disable controls based on selection"""
        has_dividers = len(self.dividers) > 0
        has_selection = self.current_divider_name is not None
        
        self.divider_combo.setEnabled(has_dividers)
        self.remove_button.setEnabled(has_selection)
        self.position_slider.setEnabled(has_selection)
        self.probability_slider.setEnabled(has_selection)
        self.color_button.setEnabled(has_selection)
        
        if has_selection:
            self.update_property_controls()
    
    def update_property_controls(self):
        """Update property controls with current divider values"""
        divider = self.get_current_divider()
        if divider:
            self.position_slider.set_value(divider['x'])
            self.probability_slider.set_value(divider.get('probability', 0.1))
            self.color_button.set_color(divider.get('color', '#FF5722'))
    
    def get_current_divider(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected divider"""
        if not self.current_divider_name:
            return None
        
        for divider in self.dividers:
            if divider['name'] == self.current_divider_name:
                return divider
        return None
    
    def on_divider_selected(self, name: str):
        """Handle divider selection change"""
        self.current_divider_name = name if name else None
        self.update_controls_state()
        if self.current_divider_name:
            self.dividerSelected.emit(self.current_divider_name)
    
    def on_position_changed(self, value: float):
        """Handle position slider change"""
        if self.current_divider_name:
            divider = self.get_current_divider()
            if divider:
                divider['x'] = value
                self.dividerChanged.emit()
    
    def on_probability_changed(self, value: float):
        """Handle probability slider change"""
        if self.current_divider_name:
            divider = self.get_current_divider()
            if divider:
                divider['probability'] = value
                self.dividerChanged.emit()
    
    def on_color_changed(self, color: str):
        """Handle color button change"""
        if self.current_divider_name:
            divider = self.get_current_divider()
            if divider:
                divider['color'] = color
                self.dividerChanged.emit()
    
    def create_new_divider(self):
        """Create a new divider"""
        name, ok = QtWidgets.QInputDialog.getText(
            self, 'New Divider', 'Enter divider name:'
        )
        
        if ok and name.strip():
            name = name.strip()
            
            # Check if name already exists
            existing_names = [d['name'] for d in self.dividers]
            if name in existing_names:
                QtWidgets.QMessageBox.warning(
                    self, 'Error', f'Divider "{name}" already exists.'
                )
                return
            
            # Create new divider
            new_divider = {
                'name': name,
                'x': 150,  # Default position
                'probability': 0.1,
                'color': '#FF5722'
            }
            
            self.dividers.append(new_divider)
            self.update_divider_combo()
            
            # Select the new divider
            self.divider_combo.setCurrentText(name)
            self.current_divider_name = name
            self.update_controls_state()
            
            self.dividerChanged.emit()
    
    def remove_current_divider(self):
        """Remove the currently selected divider"""
        if not self.current_divider_name:
            return
        
        reply = QtWidgets.QMessageBox.question(
            self, 'Confirm Removal', 
            f'Remove divider "{self.current_divider_name}"?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Remove divider
            self.dividers = [d for d in self.dividers if d['name'] != self.current_divider_name]
            self.current_divider_name = None
            
            self.update_divider_combo()
            self.update_controls_state()
            
            self.dividerChanged.emit()
    
    def set_position_range(self, min_x: float, max_x: float):
        """Set the valid range for divider positions"""
        self.position_slider.set_range(min_x, max_x)


class SpawnerControlPanel(QtWidgets.QWidget):
    """Spawner parameter controls"""
    
    spawnerChanged = QtCore.pyqtSignal()  # Emitted when spawner parameters change
    
    def __init__(self, parent=None):
        """Initialize spawner control panel"""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
        self.count_slider = ParameterSlider("Spawn Count:", 1, 10, 3, decimals=0)
        self.count_slider.valueChanged.connect(self.spawnerChanged.emit)
        layout.addWidget(self.count_slider)
        
        self.interval_slider = ParameterSlider("Spawn Interval:", 1, 20, 5, decimals=0)
        self.interval_slider.valueChanged.connect(self.spawnerChanged.emit)
        layout.addWidget(self.interval_slider)
    
    def set_values(self, count: int, interval: int):
        """Set spawner values"""
        self.count_slider.set_value(count)
        self.interval_slider.set_value(interval)
    
    def get_values(self) -> tuple:
        """Get current spawner values as (count, interval)"""
        return (int(self.count_slider.get_value()), int(self.interval_slider.get_value()))


class StepControlPanel(QtWidgets.QWidget):
    """Step function controls"""
    
    parameterChanged = QtCore.pyqtSignal()  # Emitted when step parameters change
    autoStepToggled = QtCore.pyqtSignal(bool)  # Emitted when auto-step is toggled
    
    def __init__(self, parent=None):
        """Initialize step control panel"""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Auto-step control
        auto_layout = QtWidgets.QHBoxLayout()
        
        self.auto_checkbox = QtWidgets.QCheckBox("Auto Step")
        self.auto_checkbox.toggled.connect(self.autoStepToggled.emit)
        auto_layout.addWidget(self.auto_checkbox)
        
        auto_layout.addStretch()
        layout.addLayout(auto_layout)
        
        # Step parameters
        self.decay_slider = ParameterSlider("Decay Rate:", 0, 0.1, 0.02, decimals=3)
        self.decay_slider.valueChanged.connect(self.parameterChanged.emit)
        layout.addWidget(self.decay_slider)
        
        self.interval_slider = ParameterSlider("Step Interval:", 50, 2000, 100, decimals=0)
        self.interval_slider.valueChanged.connect(self.parameterChanged.emit)
        layout.addWidget(self.interval_slider)
    
    def set_values(self, decay_rate: float, interval: int, auto_step: bool):
        """Set step control values"""
        self.decay_slider.set_value(decay_rate)
        self.interval_slider.set_value(interval)
        self.auto_checkbox.setChecked(auto_step)
    
    def get_values(self) -> tuple:
        """Get current values as (decay_rate, interval, auto_step)"""
        return (
            self.decay_slider.get_value(),
            int(self.interval_slider.get_value()),
            self.auto_checkbox.isChecked()
        )
