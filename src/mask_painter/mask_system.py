"""
Mask and grid system for the mask painter application.
Handles the grid-based mask for tracking particle exposure and cell catching.
"""

import numpy as np
import os
from typing import Dict, Any, Tuple, Optional


class MaskSystem:
    """Manages the grid-based mask system for particle tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the mask system.
        
        Args:
            config: Configuration dictionary containing system parameters
        """
        self.config = config
        self.mask_grid = None
        self.particle_count_mask = None
        
        # Grid parameters
        system_config = config.get('system', {})
        self.mask_resolution = system_config.get('mask_resolution', 100)
        self.grid_padding = system_config.get('grid_padding', 0)
        self.count_particles = system_config.get('count_particles', True)
        
        # Ellipse parameters
        ellipse_config = config.get('ellipse', {})
        self.center_x = ellipse_config.get('center_x', 150)
        self.center_y = ellipse_config.get('center_y', 100)
        self.radius_x = ellipse_config.get('radius_x', 150)
        self.radius_y = ellipse_config.get('radius_y', 50)
        
        # Grid coordinate mapping
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.grid_size_x = None
        self.grid_size_y = None
        
        # Create initial mask
        self.create_mask_grid()
    
    def create_mask_grid(self) -> None:
        """Create the mask grid based on ellipse parameters"""
        # Calculate grid bounds
        self.x_min = self.center_x - self.radius_x - self.grid_padding
        self.x_max = self.center_x + self.radius_x + self.grid_padding
        self.y_min = self.center_y - self.radius_y - self.grid_padding
        self.y_max = self.center_y + self.radius_y + self.grid_padding
        
        # Calculate grid dimensions
        self.grid_size_x = int(self.mask_resolution)
        self.grid_size_y = int(self.mask_resolution * (self.y_max - self.y_min) / (self.x_max - self.x_min))
        
        # Initialize masks
        self.mask_grid = np.zeros((self.grid_size_y, self.grid_size_x), dtype=np.float32)
        
        if self.count_particles:
            self.particle_count_mask = np.zeros((self.grid_size_y, self.grid_size_x), dtype=np.int32)
    
    def is_inside_ellipse(self, x: float, y: float) -> bool:
        """
        Check if a point is inside the ellipse.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if point is inside the ellipse
        """
        dx = x - self.center_x
        dy = y - self.center_y
        
        # Ellipse equation: (dx/rx)^2 + (dy/ry)^2 <= 1
        ellipse_value = (dx / self.radius_x) ** 2 + (dy / self.radius_y) ** 2
        return ellipse_value <= 1.0
    
    def coord_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to grid indices.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            
        Returns:
            Tuple of (grid_y, grid_x) indices, or (-1, -1) if outside grid
        """
        if (x < self.x_min or x > self.x_max or 
            y < self.y_min or y > self.y_max):
            return (-1, -1)
        
        # Convert to grid coordinates
        grid_x = int((x - self.x_min) / (self.x_max - self.x_min) * self.grid_size_x)
        grid_y = int((y - self.y_min) / (self.y_max - self.y_min) * self.grid_size_y)
        
        # Clamp to valid range
        grid_x = max(0, min(self.grid_size_x - 1, grid_x))
        grid_y = max(0, min(self.grid_size_y - 1, grid_y))
        
        return (grid_y, grid_x)
    
    def grid_to_coord(self, grid_y: int, grid_x: int) -> Tuple[float, float]:
        """
        Convert grid indices to world coordinates.
        
        Args:
            grid_y: Grid Y index
            grid_x: Grid X index
            
        Returns:
            Tuple of (world_x, world_y) coordinates
        """
        world_x = self.x_min + (grid_x / self.grid_size_x) * (self.x_max - self.x_min)
        world_y = self.y_min + (grid_y / self.grid_size_y) * (self.y_max - self.y_min)
        return (world_x, world_y)
    
    def try_catch_particle_by_cell(self, particle_x: float, particle_y: float, 
                                  catch_params: Dict[str, Any]) -> bool:
        """
        Try to catch a particle using cell-based catching logic.
        
        Args:
            particle_x: Particle X position
            particle_y: Particle Y position
            catch_params: Dictionary containing catch parameters
            
        Returns:
            True if particle was caught
        """
        # Check if particle is inside ellipse
        if not self.is_inside_ellipse(particle_x, particle_y):
            return False
        
        # Get catch parameters
        catch_probability = catch_params.get('probability', 0.05)
        catch_radius = catch_params.get('radius', 3.0)
        catch_exposure = catch_params.get('exposure', 0.2)
        
        # Check if particle is caught by random probability
        if np.random.random() > catch_probability:
            return False
        
        # Apply exposure in a radius around the particle
        self._apply_exposure_circle(particle_x, particle_y, catch_radius, catch_exposure)
        
        # Count particle if enabled
        if self.count_particles and self.particle_count_mask is not None:
            grid_y, grid_x = self.coord_to_grid(particle_x, particle_y)
            if grid_y >= 0 and grid_x >= 0:
                self.particle_count_mask[grid_y, grid_x] += 1
        
        return True
    
    def _apply_exposure_circle(self, center_x: float, center_y: float, 
                              radius: float, exposure: float) -> None:
        """
        Apply exposure in a circular area around a point.
        
        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Radius of exposure area
            exposure: Exposure amount to add
        """
        # Convert center to grid coordinates
        center_grid_y, center_grid_x = self.coord_to_grid(center_x, center_y)
        if center_grid_y < 0 or center_grid_x < 0:
            return
        
        # Calculate grid radius
        radius_grid_x = int(radius / (self.x_max - self.x_min) * self.grid_size_x) + 1
        radius_grid_y = int(radius / (self.y_max - self.y_min) * self.grid_size_y) + 1
        
        # Apply exposure in a circular pattern
        for dy in range(-radius_grid_y, radius_grid_y + 1):
            for dx in range(-radius_grid_x, radius_grid_x + 1):
                grid_y = center_grid_y + dy
                grid_x = center_grid_x + dx
                
                # Check bounds
                if (0 <= grid_y < self.grid_size_y and 
                    0 <= grid_x < self.grid_size_x):
                    
                    # Check if within circular radius
                    world_x, world_y = self.grid_to_coord(grid_y, grid_x)
                    distance = np.sqrt((world_x - center_x)**2 + (world_y - center_y)**2)
                    
                    if distance <= radius:
                        # Only paint inside ellipse
                        if self.is_inside_ellipse(world_x, world_y):
                            self.mask_grid[grid_y, grid_x] += exposure
    
    def apply_decay(self, decay_rate: float, saturation_threshold: float = 0.95) -> None:
        """
        Apply decay to the mask grid.
        
        Args:
            decay_rate: Rate of decay per step
            saturation_threshold: Threshold above which no decay occurs
        """
        if self.mask_grid is not None:
            # Apply decay only to cells below saturation threshold
            decay_mask = self.mask_grid < saturation_threshold
            self.mask_grid[decay_mask] *= (1.0 - decay_rate)
            
            # Clamp negative values to zero
            self.mask_grid = np.maximum(self.mask_grid, 0.0)
    
    def reset_mask(self) -> None:
        """Reset the mask grid to zeros"""
        if self.mask_grid is not None:
            self.mask_grid.fill(0.0)
        
        if self.particle_count_mask is not None:
            self.particle_count_mask.fill(0)
    
    def get_mask_data(self) -> np.ndarray:
        """Get the current mask data"""
        return self.mask_grid.copy() if self.mask_grid is not None else np.array([])
    
    def get_particle_count_data(self) -> Optional[np.ndarray]:
        """Get the particle count mask data"""
        return (self.particle_count_mask.copy() 
                if self.particle_count_mask is not None else None)
    
    def get_grid_bounds(self) -> Tuple[float, float, float, float]:
        """Get grid bounds as (x_min, x_max, y_min, y_max)"""
        return (self.x_min, self.x_max, self.y_min, self.y_max)
    
    def get_grid_dimensions(self) -> Tuple[int, int]:
        """Get grid dimensions as (width, height)"""
        return (self.grid_size_x, self.grid_size_y)
    
    def save_mask(self, filepath: str) -> bool:
        """
        Save mask data to file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if save was successful
        """
        try:
            if self.mask_grid is not None:
                np.save(filepath, self.mask_grid)
                return True
        except Exception as e:
            print(f"Error saving mask: {e}")
        return False
    
    def load_mask(self, filepath: str) -> bool:
        """
        Load mask data from file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            True if load was successful
        """
        try:
            if os.path.exists(filepath):
                loaded_mask = np.load(filepath)
                if loaded_mask.shape == (self.grid_size_y, self.grid_size_x):
                    self.mask_grid = loaded_mask.astype(np.float32)
                    return True
                else:
                    print(f"Mask shape mismatch: expected {(self.grid_size_y, self.grid_size_x)}, got {loaded_mask.shape}")
        except Exception as e:
            print(f"Error loading mask: {e}")
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current mask.
        
        Returns:
            Dictionary with mask statistics
        """
        if self.mask_grid is None:
            return {
                'total_cells': 0,
                'painted_cells': 0,
                'coverage_percentage': 0,
                'average_exposure': 0,
                'max_exposure': 0
            }
        
        # Count cells inside ellipse
        total_inside_ellipse = 0
        painted_inside_ellipse = 0
        
        for grid_y in range(self.grid_size_y):
            for grid_x in range(self.grid_size_x):
                world_x, world_y = self.grid_to_coord(grid_y, grid_x)
                if self.is_inside_ellipse(world_x, world_y):
                    total_inside_ellipse += 1
                    if self.mask_grid[grid_y, grid_x] > 0:
                        painted_inside_ellipse += 1
        
        # Calculate statistics
        nonzero_mask = self.mask_grid[self.mask_grid > 0]
        
        coverage_percentage = (painted_inside_ellipse / total_inside_ellipse * 100 
                             if total_inside_ellipse > 0 else 0)
        
        return {
            'total_cells': total_inside_ellipse,
            'painted_cells': painted_inside_ellipse,
            'coverage_percentage': coverage_percentage,
            'average_exposure': np.mean(nonzero_mask) if len(nonzero_mask) > 0 else 0,
            'max_exposure': np.max(self.mask_grid),
            'grid_dimensions': (self.grid_size_x, self.grid_size_y)
        }
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration and recreate mask if necessary.
        
        Args:
            config: New configuration dictionary
        """
        old_ellipse = (self.center_x, self.center_y, self.radius_x, self.radius_y)
        old_resolution = self.mask_resolution
        
        # Update configuration
        self.config = config
        
        # Update parameters
        system_config = config.get('system', {})
        self.mask_resolution = system_config.get('mask_resolution', 100)
        self.grid_padding = system_config.get('grid_padding', 0)
        self.count_particles = system_config.get('count_particles', True)
        
        ellipse_config = config.get('ellipse', {})
        self.center_x = ellipse_config.get('center_x', 150)
        self.center_y = ellipse_config.get('center_y', 100)
        self.radius_x = ellipse_config.get('radius_x', 150)
        self.radius_y = ellipse_config.get('radius_y', 50)
        
        # Check if we need to recreate the mask
        new_ellipse = (self.center_x, self.center_y, self.radius_x, self.radius_y)
        if old_ellipse != new_ellipse or old_resolution != self.mask_resolution:
            self.create_mask_grid()