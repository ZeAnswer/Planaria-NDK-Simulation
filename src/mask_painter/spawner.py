"""
Particle spawner system for the mask painter application.
Handles spawning particles at regular intervals from a specific location.
"""

from typing import Dict, Any, Optional, Tuple


class ParticleSpawner:
    """Manages spawning particles at regular intervals from a specific location"""
    
    def __init__(self, spawn_count: int = 1, spawn_interval: int = 5):
        """
        Initialize the particle spawner.
        
        Args:
            spawn_count: Number of particles to spawn at each interval
            spawn_interval: Number of steps between spawns
        """
        self.x = 0  # Initial position, will be updated
        self.y = 0  # Initial position, will be updated
        self.spawn_count = max(1, spawn_count)
        self.spawn_interval = max(1, spawn_interval)
        self.step_counter = 0
        
    def update_position(self, ellipse_center_x: float, ellipse_radius_x: float, ellipse_center_y: float) -> None:
        """
        Updates the spawner's position to be at the rightmost tip of the ellipse.
        """
        self.x = ellipse_center_x + ellipse_radius_x
        self.y = ellipse_center_y
    
    def get_position(self) -> Tuple[float, float]:
        """Get the spawner's current position"""
        return (self.x, self.y)
    
    def set_spawn_count(self, count: int) -> None:
        """
        Set number of particles to spawn per event.
        
        Args:
            count: Number of particles (must be >= 1)
        """
        self.spawn_count = max(1, count)
    
    def get_spawn_count(self) -> int:
        """Get current spawn count"""
        return self.spawn_count
    
    def set_spawn_interval(self, interval: int) -> None:
        """
        Set interval between spawning events.
        
        Args:
            interval: Steps between spawns (must be >= 1)
        """
        self.spawn_interval = max(1, interval)
    
    def get_spawn_interval(self) -> int:
        """Get current spawn interval"""
        return self.spawn_interval
    
    def should_spawn(self, current_step: Optional[int] = None) -> bool:
        """
        Check if it's time to spawn particles.
        
        Args:
            current_step: Optional current step counter (uses internal if None)
            
        Returns:
            True if particles should be spawned this step
        """
        if current_step is not None:
            return current_step % self.spawn_interval == 0
        else:
            self.step_counter += 1
            return self.step_counter % self.spawn_interval == 0
    
    def reset_step_counter(self) -> None:
        """Reset the internal step counter"""
        self.step_counter = 0
    
    def force_spawn(self) -> bool:
        """
        Force immediate spawning (resets counter).
        
        Returns:
            True (spawning should occur)
        """
        self.step_counter = 0
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive spawner status.
        
        Returns:
            Dictionary with spawner status information
        """
        return {
            'position': (self.x, self.y),
            'spawn_count': self.spawn_count,
            'spawn_interval': self.spawn_interval,
            'step_counter': self.step_counter,
            'next_spawn_in': self.spawn_interval - (self.step_counter % self.spawn_interval)
        }
    
    def update_from_config(self, config: Dict[str, Any]) -> None:
        """
        Update spawner parameters from configuration.
        
        Args:
            config: Configuration dictionary containing spawner parameters
        """
        spawner_config = config.get('spawner', {})
        
        self.set_spawn_count(spawner_config.get('spawn_count', self.spawn_count))
        self.set_spawn_interval(spawner_config.get('spawn_interval', self.spawn_interval))
        
        # If ellipse info is available, update position
        ellipse_config = config.get('ellipse', {})
        center_x = ellipse_config.get('center_x')
        radius_x = ellipse_config.get('radius_x')
        center_y = ellipse_config.get('center_y')
        
        if all(v is not None for v in [center_x, radius_x, center_y]):
            self.update_position(center_x, radius_x, center_y)