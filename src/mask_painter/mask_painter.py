"""
Main application for the planaria particle simulator and mask painter.
Refactored version with modular components.
"""

import sys
import os
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# Import our modular components
from config_manager import ConfigManager
from particle import ParticleManager
from spawner import ParticleSpawner
from divider import DividerManager
from mask_system import MaskSystem
from visualization import VisualizationManager
from ui_components import (
    ParameterSlider, ColorButton, DividerControlPanel, 
    SpawnerControlPanel, StepControlPanel
)


class MaskPainter(QtWidgets.QMainWindow):
    """Main application window for the mask painter"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.particle_manager = None
        self.spawner = None
        self.divider_manager = None
        self.mask_system = None
        self.visualization_manager = None
        
        # UI state
        self.auto_step_active = False
        self.step_counter = 0
        
        # Timer for auto-stepping
        self.step_timer = QtCore.QTimer()
        self.step_timer.timeout.connect(self.perform_step)
        
        # Load configuration and initialize systems
        self.load_current_profile()
        
        # Setup UI
        self.setup_ui()
        self.setup_graphics()
        self.connect_signals()
        
        # Initial visualization update
        self.update_all_visualizations()
    
    def load_current_profile(self):
        """Load the current profile and initialize all systems"""
        current_profile = self.config_manager.get_current_profile_name()
        config = self.config_manager.merge_profile_config(current_profile)
        
        # Initialize all managers with the configuration
        self.particle_manager = ParticleManager(config)
        
        # Initialize spawner
        spawner_config = config.get('spawner', {})
        self.spawner = ParticleSpawner(
            x=spawner_config.get('x', 150),
            y=spawner_config.get('y', 100),
            spawn_count=spawner_config.get('spawn_count', 3),
            spawn_interval=spawner_config.get('spawn_interval', 5)
        )
        
        # Initialize divider manager
        ellipse_config = config.get('ellipse', {})
        ellipse_bounds = (
            ellipse_config.get('center_x', 150),
            ellipse_config.get('center_y', 100),
            ellipse_config.get('radius_x', 150),
            ellipse_config.get('radius_y', 50)
        )
        self.divider_manager = DividerManager(config, ellipse_bounds)
        
        # Initialize mask system
        self.mask_system = MaskSystem(config)
        
        self.current_config = config
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Planaria Particle Simulator")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QtWidgets.QWidget()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(350)
        main_layout.addWidget(left_panel)
        
        # Right panel for visualization
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)
        
        # Setup left panel
        self.setup_control_panel(left_panel)
    
    def setup_control_panel(self, parent):
        """Setup the control panel with all UI components"""
        layout = QtWidgets.QVBoxLayout(parent)
        
        # Profile selection
        profile_group = QtWidgets.QGroupBox("Profile Management")
        profile_layout = QtWidgets.QVBoxLayout(profile_group)
        
        profile_select_layout = QtWidgets.QHBoxLayout()
        profile_select_layout.addWidget(QtWidgets.QLabel("Profile:"))
        
        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.addItems(self.config_manager.get_available_profiles())
        self.profile_combo.setCurrentText(self.config_manager.get_current_profile_name())
        profile_select_layout.addWidget(self.profile_combo)
        
        profile_layout.addLayout(profile_select_layout)
        
        profile_buttons_layout = QtWidgets.QHBoxLayout()
        self.save_profile_btn = QtWidgets.QPushButton("Save Profile")
        self.load_profile_btn = QtWidgets.QPushButton("Load Profile")
        profile_buttons_layout.addWidget(self.save_profile_btn)
        profile_buttons_layout.addWidget(self.load_profile_btn)
        profile_layout.addLayout(profile_buttons_layout)
        
        layout.addWidget(profile_group)
        
        # Step controls
        step_group = QtWidgets.QGroupBox("Step Controls")
        step_layout = QtWidgets.QVBoxLayout(step_group)
        
        step_buttons_layout = QtWidgets.QHBoxLayout()
        self.step_btn = QtWidgets.QPushButton("Step")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        step_buttons_layout.addWidget(self.step_btn)
        step_buttons_layout.addWidget(self.clear_btn)
        step_layout.addLayout(step_buttons_layout)
        
        self.step_controls = StepControlPanel()
        step_layout.addWidget(self.step_controls)
        
        layout.addWidget(step_group)
        
        # Particle controls
        particle_group = QtWidgets.QGroupBox("Particle Parameters")
        particle_layout = QtWidgets.QVBoxLayout(particle_group)
        
        self.velocity_slider = ParameterSlider("Velocity:", 1, 50, 10, decimals=1)
        particle_layout.addWidget(self.velocity_slider)
        
        self.catch_prob_slider = ParameterSlider("Catch Probability:", 0, 1, 0.05, decimals=3)
        particle_layout.addWidget(self.catch_prob_slider)
        
        self.catch_radius_slider = ParameterSlider("Catch Radius:", 1, 20, 3, decimals=1)
        particle_layout.addWidget(self.catch_radius_slider)
        
        self.catch_exposure_slider = ParameterSlider("Catch Exposure:", 0, 1, 0.2, decimals=3)
        particle_layout.addWidget(self.catch_exposure_slider)
        
        layout.addWidget(particle_group)
        
        # Spawner controls
        spawner_group = QtWidgets.QGroupBox("Spawner Parameters")
        spawner_layout = QtWidgets.QVBoxLayout(spawner_group)
        
        self.spawner_controls = SpawnerControlPanel()
        spawner_layout.addWidget(self.spawner_controls)
        
        layout.addWidget(spawner_group)
        
        # Divider controls
        divider_group = QtWidgets.QGroupBox("Divider Management")
        divider_layout = QtWidgets.QVBoxLayout(divider_group)
        
        self.divider_controls = DividerControlPanel()
        divider_layout.addWidget(self.divider_controls)
        
        layout.addWidget(divider_group)
        
        layout.addStretch()
    
    def setup_graphics(self):
        """Setup the graphics visualization"""
        self.visualization_manager = VisualizationManager(
            self.plot_widget, 
            self.current_config
        )
        
        # Connect mouse click event
        self.plot_widget.scene().sigMouseClicked.connect(self.mouse_clicked)
    
    def connect_signals(self):
        """Connect all UI signals to their handlers"""
        # Profile management
        self.save_profile_btn.clicked.connect(self.save_current_profile)
        self.load_profile_btn.clicked.connect(self.load_selected_profile)
        
        # Step controls
        self.step_btn.clicked.connect(self.perform_step)
        self.clear_btn.clicked.connect(self.clear_simulation)
        self.step_controls.parameterChanged.connect(self.update_step_parameters)
        self.step_controls.autoStepToggled.connect(self.toggle_auto_step)
        
        # Particle parameters
        self.velocity_slider.valueChanged.connect(self.update_velocity)
        self.catch_prob_slider.valueChanged.connect(self.update_catch_probability)
        self.catch_radius_slider.valueChanged.connect(self.update_catch_radius)
        self.catch_exposure_slider.valueChanged.connect(self.update_catch_exposure)
        
        # Spawner controls
        self.spawner_controls.spawnerChanged.connect(self.update_spawner_parameters)
        
        # Divider controls
        self.divider_controls.dividerChanged.connect(self.update_divider_parameters)
        
        # Load initial values into UI
        self.load_ui_values_from_config()
    
    def load_ui_values_from_config(self):
        """Load current configuration values into UI controls"""
        config = self.current_config
        
        # Particle parameters
        particles_config = config.get('particles', {})
        self.velocity_slider.set_value(particles_config.get('velocity', 10.0))
        
        catching_config = config.get('catching', {})
        self.catch_prob_slider.set_value(catching_config.get('probability', 0.05))
        self.catch_radius_slider.set_value(catching_config.get('radius', 3.0))
        self.catch_exposure_slider.set_value(catching_config.get('exposure', 0.2))
        
        # Step parameters
        step_config = config.get('step_function', {})
        self.step_controls.set_values(
            step_config.get('decay_rate', 0.02),
            step_config.get('step_interval', 100),
            False  # Auto-step starts disabled
        )
        
        # Spawner parameters
        spawner_config = config.get('spawner', {})
        self.spawner_controls.set_values(
            spawner_config.get('spawn_count', 3),
            spawner_config.get('spawn_interval', 5)
        )
        
        # Divider parameters
        dividers = config.get('dividers', [])
        self.divider_controls.set_dividers(dividers)
        
        # Set divider position range based on ellipse
        ellipse_config = config.get('ellipse', {})
        center_x = ellipse_config.get('center_x', 150)
        radius_x = ellipse_config.get('radius_x', 150)
        self.divider_controls.set_position_range(center_x - radius_x, center_x + radius_x)
    
    def mouse_clicked(self, event):
        """Handle mouse clicks for spawner placement"""
        if event.button() == QtCore.Qt.LeftButton:
            # Convert click position to data coordinates
            scene_pos = event.scenePos()
            view_pos = self.plot_widget.plotItem.vb.mapSceneToView(scene_pos)
            
            x, y = view_pos.x(), view_pos.y()
            
            # Check if click is inside ellipse
            if self.mask_system.is_inside_ellipse(x, y):
                # Move spawner to clicked position
                self.spawner.set_position(x, y)
                
                # Update spawner configuration
                self.current_config['spawner']['x'] = x
                self.current_config['spawner']['y'] = y
                
                # Update visualization
                self.visualization_manager.update_spawner_display((x, y))
    
    def perform_step(self):
        """Perform one simulation step"""
        self.step_counter += 1
        
        # Check if spawner should spawn particles
        if self.spawner.should_spawn():
            spawn_count = self.spawner.get_spawn_count()
            spawner_pos = self.spawner.get_position()
            velocity = self.current_config.get('particles', {}).get('velocity', 10.0)
            
            # Spawn particles
            self.particle_manager.spawn_multiple_particles(
                spawner_pos[0], spawner_pos[1], spawn_count, velocity
            )
        
        # Move all particles
        self.particle_manager.move_all_particles()
        
        # Process particle catching
        self.process_particle_catching()
        
        # Remove expired particles
        self.particle_manager.remove_expired_particles()
        
        # Apply decay to mask
        step_config = self.current_config.get('step_function', {})
        decay_rate = step_config.get('decay_rate', 0.02)
        saturation_threshold = step_config.get('saturation_threshold', 0.95)
        self.mask_system.apply_decay(decay_rate, saturation_threshold)
        
        # Update visualizations
        self.update_particle_visualization()
        self.update_mask_visualization()
    
    def process_particle_catching(self):
        """Process particle catching logic"""
        catching_config = self.current_config.get('catching', {})
        particles_to_remove = []
        
        for particle in self.particle_manager.get_particles():
            particle_caught = False
            
            # Check region-based catching (dividers)
            region_probability = self.divider_manager.get_region_probability(particle.x)
            if region_probability > 0 and np.random.random() < region_probability:
                particle_caught = True
            
            # Check cell-based catching if not caught by region
            if not particle_caught:
                if self.mask_system.try_catch_particle_by_cell(
                    particle.x, particle.y, catching_config
                ):
                    particle_caught = True
            
            # Remove caught particles
            if particle_caught:
                particles_to_remove.append(particle)
        
        # Remove caught particles
        for particle in particles_to_remove:
            self.particle_manager.remove_particle(particle)
    
    def clear_simulation(self):
        """Clear all particles and reset simulation"""
        self.particle_manager.clear_all_particles()
        self.mask_system.reset_mask()
        self.step_counter = 0
        self.spawner.reset_step_counter()
        
        # Update visualizations
        self.update_all_visualizations()
    
    def toggle_auto_step(self, enabled):
        """Toggle automatic stepping"""
        self.auto_step_active = enabled
        
        if enabled:
            step_config = self.current_config.get('step_function', {})
            interval = step_config.get('step_interval', 100)
            self.step_timer.start(interval)
        else:
            self.step_timer.stop()
    
    def update_step_parameters(self):
        """Update step function parameters"""
        decay_rate, interval, auto_step = self.step_controls.get_values()
        
        step_config = self.current_config.setdefault('step_function', {})
        step_config['decay_rate'] = decay_rate
        step_config['step_interval'] = interval
        
        # Update timer interval if auto-step is active
        if self.auto_step_active:
            self.step_timer.setInterval(interval)
    
    def update_velocity(self, value):
        """Update particle velocity"""
        self.current_config.setdefault('particles', {})['velocity'] = value
        self.particle_manager.update_config(self.current_config)
    
    def update_catch_probability(self, value):
        """Update catch probability"""
        self.current_config.setdefault('catching', {})['probability'] = value
    
    def update_catch_radius(self, value):
        """Update catch radius"""
        self.current_config.setdefault('catching', {})['radius'] = value
    
    def update_catch_exposure(self, value):
        """Update catch exposure"""
        self.current_config.setdefault('catching', {})['exposure'] = value
    
    def update_spawner_parameters(self):
        """Update spawner parameters"""
        count, interval = self.spawner_controls.get_values()
        
        self.spawner.set_spawn_count(count)
        self.spawner.set_spawn_interval(interval)
        
        spawner_config = self.current_config.setdefault('spawner', {})
        spawner_config['spawn_count'] = count
        spawner_config['spawn_interval'] = interval
    
    def update_divider_parameters(self):
        """Update divider parameters"""
        dividers = self.divider_controls.dividers
        self.current_config['dividers'] = dividers
        
        # Update divider manager
        ellipse_config = self.current_config.get('ellipse', {})
        ellipse_bounds = (
            ellipse_config.get('center_x', 150),
            ellipse_config.get('center_y', 100),
            ellipse_config.get('radius_x', 150),
            ellipse_config.get('radius_y', 50)
        )
        self.divider_manager = DividerManager(self.current_config, ellipse_bounds)
        
        # Update visualization
        self.visualization_manager.update_divider_display(dividers, ellipse_bounds)
    
    def save_current_profile(self):
        """Save current state as a profile"""
        profile_name = self.profile_combo.currentText()
        
        # Create profile data from current configuration
        profile_data = {
            'ellipse': self.current_config.get('ellipse', {}),
            'particles': self.current_config.get('particles', {}),
            'spawner': self.current_config.get('spawner', {}),
            'catching': self.current_config.get('catching', {}),
            'step_function': self.current_config.get('step_function', {}),
            'system': self.current_config.get('system', {}),
            'dividers': self.current_config.get('dividers', []),
            'ui_ranges': self.current_config.get('ui_ranges', {})
        }
        
        # Save profile
        if self.config_manager.save_profile(profile_name, profile_data):
            QtWidgets.QMessageBox.information(
                self, "Success", f"Profile '{profile_name}' saved successfully."
            )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", f"Failed to save profile '{profile_name}'."
            )
    
    def load_selected_profile(self):
        """Load the selected profile"""
        profile_name = self.profile_combo.currentText()
        
        try:
            # Load new configuration
            new_config = self.config_manager.merge_profile_config(profile_name)
            self.current_config = new_config
            
            # Update all systems
            self.particle_manager.update_config(new_config)
            self.spawner.update_from_config(new_config)
            
            ellipse_config = new_config.get('ellipse', {})
            ellipse_bounds = (
                ellipse_config.get('center_x', 150),
                ellipse_config.get('center_y', 100),
                ellipse_config.get('radius_x', 150),
                ellipse_config.get('radius_y', 50)
            )
            self.divider_manager = DividerManager(new_config, ellipse_bounds)
            self.mask_system.update_config(new_config)
            self.visualization_manager.update_config(new_config)
            
            # Update UI values
            self.load_ui_values_from_config()
            
            # Clear simulation and update visualizations
            self.clear_simulation()
            
            # Set as current profile
            self.config_manager.set_current_profile(profile_name)
            
            QtWidgets.QMessageBox.information(
                self, "Success", f"Profile '{profile_name}' loaded successfully."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error", f"Failed to load profile '{profile_name}': {str(e)}"
            )
    
    def update_particle_visualization(self):
        """Update particle visualization"""
        positions = self.particle_manager.get_particle_positions()
        self.visualization_manager.update_particle_display(positions)
    
    def update_mask_visualization(self):
        """Update mask visualization"""
        mask_data = self.mask_system.get_mask_data()
        grid_bounds = self.mask_system.get_grid_bounds()
        self.visualization_manager.update_mask_display(mask_data, grid_bounds)
    
    def update_all_visualizations(self):
        """Update all visualization components"""
        # Update particle display
        self.update_particle_visualization()
        
        # Update mask display
        self.update_mask_visualization()
        
        # Update spawner display
        spawner_pos = self.spawner.get_position()
        self.visualization_manager.update_spawner_display(spawner_pos)
        
        # Update divider display
        ellipse_config = self.current_config.get('ellipse', {})
        ellipse_bounds = (
            ellipse_config.get('center_x', 150),
            ellipse_config.get('center_y', 100),
            ellipse_config.get('radius_x', 150),
            ellipse_config.get('radius_y', 50)
        )
        dividers = self.current_config.get('dividers', [])
        self.visualization_manager.update_divider_display(dividers, ellipse_bounds)


def main():
    """Main function to create and run the application"""
    app = QtWidgets.QApplication(sys.argv)
    
    app.setApplicationName("Mask Painter")
    app.setOrganizationName("PlanariaLab")
    
    # Create and show the main window
    window = MaskPainter()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
