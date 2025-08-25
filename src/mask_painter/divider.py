"""
Divider system for the mask painter application.
Handles vertical dividers that segment the planaria and affect particle catching.
"""

from typing import List, Dict, Any, Optional, Tuple


class Divider:
    """A vertical divider that segments the planaria"""
    
    def __init__(self, name: str, x: float, probability: float = 0.1, 
                 color: str = '#FF5722'):
        """
        Initialize a divider.
        
        Args:
            name: Human-readable name for the divider
            x: X position of the vertical divider line
            probability: Region catch probability for particles to the right
            color: Color for visualization (hex string)
        """
        self.name = name
        self.x = x
        self.probability = probability
        self.color = color
    
    def is_point_in_region(self, point_x: float) -> bool:
        """
        Check if a point is in this divider's region;
        Meaning if a point is to the right of the divider
        
        Args:
            point_x: X coordinate to check
            
        Returns:
            True if point is in this divider's affected region
        """
        return point_x > self.x
    
    def get_catch_probability(self) -> float:
        """Get the catch probability for this divider's region"""
        return self.probability
    
    def set_position(self, x: float) -> None:
        """
        Set the divider's X position.
        
        Args:
            x: New X position
        """
        self.x = x
    
    def set_probability(self, probability: float) -> None:
        """
        Set the region catch probability.
        
        Args:
            probability: New probability (0.0 to 1.0)
        """
        self.probability = max(0.0, min(1.0, probability))
    
    def set_color(self, color: str) -> None:
        """
        Set the visualization color.
        
        Args:
            color: Color as hex string (e.g., '#FF5722')
        """
        self.color = color
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get divider configuration as dictionary.
        
        Returns:
            Dictionary with divider configuration
        """
        return {
            'name': self.name,
            'x': self.x,
            'probability': self.probability,
            'color': self.color
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update divider from configuration dictionary.
        
        Args:
            config_dict: Dictionary with divider configuration
        """
        if 'x' in config_dict:
            self.x = config_dict['x']
        if 'probability' in config_dict:
            self.set_probability(config_dict['probability'])
        if 'color' in config_dict:
            self.color = config_dict['color']
    
    def __str__(self) -> str:
        """String representation of divider"""
        return f"Divider({self.name}, x={self.x:.1f}, p={self.probability:.3f})"


class DividerManager:
    """Manages a collection of dividers"""
    
    def __init__(self, config: Dict[str, Any], planaria_bounds: Tuple[float, float, float, float]):
        """
        Initialize the divider manager.
        
        Args:
            config: Configuration dictionary containing divider data
            planaria_bounds: (center_x, center_y, radius_x, radius_y) of ellipse
        """
        self.dividers: List[Divider] = []
        self.planaria_bounds = planaria_bounds
        self.load_from_config(config)
    
    def load_from_config(self, config: Dict[str, Any]) -> None:
        """
        Load dividers from configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.dividers.clear()
        divider_configs = config.get('dividers', [])
        
        for divider_config in divider_configs:
            if isinstance(divider_config, dict):
                name = divider_config.get('name', f'Divider {len(self.dividers) + 1}')
                x = divider_config.get('x', 0)
                probability = divider_config.get('probability', 0.1)
                color = divider_config.get('color', '#FF5722')
                
                divider = Divider(name, x, probability, color)
                self.dividers.append(divider)
    
    def add_divider(self, name: str, position: float, probability: float = 0.1, 
                   color: str = '#FF5722') -> bool:
        """
        Add a new divider.
        
        Args:
            name: Name for the divider
            position: X position
            probability: Region catch probability
            color: Visualization color
            
        Returns:
            True if divider was added successfully
        """
        # Check if name already exists
        if self.get_divider_by_name(name) is not None:
            return False
        
        # Validate position
        if not self.validate_position(position):
            return False
        
        divider = Divider(name, position, probability, color)
        self.dividers.append(divider)
        
        # Sort dividers by x position for consistent behavior
        self.dividers.sort(key=lambda d: d.x)
        
        return True
    
    def remove_divider(self, name: str) -> bool:
        """
        Remove a divider by name.
        
        Args:
            name: Name of divider to remove
            
        Returns:
            True if divider was found and removed
        """
        divider = self.get_divider_by_name(name)
        if divider:
            self.dividers.remove(divider)
            return True
        return False
    
    def get_divider_by_name(self, name: str) -> Optional[Divider]:
        """
        Get a divider by its name.
        
        Args:
            name: Name of divider to find
            
        Returns:
            Divider object or None if not found
        """
        for divider in self.dividers:
            if divider.name == name:
                return divider
        return None
    
    def get_all_dividers(self) -> List[Divider]:
        """Get list of all dividers"""
        return self.dividers.copy()
    
    def get_divider_names(self) -> List[str]:
        """Get list of all divider names"""
        return [divider.name for divider in self.dividers]
    
    def get_region_probability(self, x: float) -> float:
        """
        Get the region catch probability for a given X position.
        
        Args:
            x: X coordinate to check
            
        Returns:
            Catch probability for the region containing this point
        """
        # Find the rightmost divider that affects this position
        applicable_dividers = [d for d in self.dividers if d.is_point_in_region(x)]
        
        if not applicable_dividers:
            return 0.0  # No dividers affect this region
        
        # Return the probability of the rightmost applicable divider
        # (assuming dividers are sorted by x position)
        return applicable_dividers[-1].get_catch_probability()
    
    def validate_position(self, x: float) -> bool:
        """
        Validate that a position is within planaria bounds.
        
        Args:
            x: X position to validate
            
        Returns:
            True if position is valid
        """
        center_x, _, radius_x, _ = self.planaria_bounds
        min_x = center_x - radius_x
        max_x = center_x + radius_x
        
        return min_x <= x <= max_x
    
    def update_planaria_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
        """
        Update planaria bounds and validate existing dividers.
        
        Args:
            bounds: (center_x, center_y, radius_x, radius_y)
        """
        self.planaria_bounds = bounds
        
        # Remove dividers that are now outside bounds
        valid_dividers = []
        for divider in self.dividers:
            if self.validate_position(divider.x):
                valid_dividers.append(divider)
        
        self.dividers = valid_dividers
    
    def get_config_list(self) -> List[Dict[str, Any]]:
        """
        Get dividers configuration as list of dictionaries.
        
        Returns:
            List of divider configuration dictionaries
        """
        return [divider.get_config_dict() for divider in self.dividers]
    
    def clear_all_dividers(self) -> int:
        """
        Remove all dividers.
        
        Returns:
            Number of dividers that were removed
        """
        count = len(self.dividers)
        self.dividers.clear()
        return count
    
    def get_divider_count(self) -> int:
        """Get number of dividers"""
        return len(self.dividers)
    
    def rename_divider(self, old_name: str, new_name: str) -> bool:
        """
        Rename a divider.
        
        Args:
            old_name: Current name
            new_name: New name
            
        Returns:
            True if rename was successful
        """
        # Check if new name already exists
        if self.get_divider_by_name(new_name) is not None:
            return False
        
        divider = self.get_divider_by_name(old_name)
        if divider:
            divider.name = new_name
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about dividers.
        
        Returns:
            Dictionary with divider statistics
        """
        if not self.dividers:
            return {
                'count': 0,
                'average_probability': 0,
                'position_range': (0, 0)
            }
        
        positions = [d.x for d in self.dividers]
        probabilities = [d.probability for d in self.dividers]
        
        return {
            'count': len(self.dividers),
            'average_probability': sum(probabilities) / len(probabilities),
            'position_range': (min(positions), max(positions)),
            'names': self.get_divider_names()
        }