"""
Particle spawner system for the mask painter application.
Handles spawning particles at regular intervals from a specific location.
"""

from typing import Dict, Any, Optional, Tuple


class ParticleSpawner:
    """Manages spawning particles at regular intervals from a specific location"""
    
    def __init__(self, x: float = 0, y: float = 0, spawn_count: int = 1, 
                 spawn_interval: int = 5):
        """
        Initialize the particle spawner.
        
        Args:
            x: X position of spawner
            y: Y position of spawner
            spawn_count: Number of particles to spawn each time
            spawn_interval: Steps between spawning events
        """
        self.x = x
        self.y = y
        self.spawn_count = spawn_count
        self.spawn_interval = spawn_interval
        self.step_counter = 0
        self.is_active = True
        
    def set_position(self, x: float, y: float) -> None:
        """
        Set the spawner position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
    
    def get_position(self) -> Tuple[float, float]:
        """Get spawner position as tuple"""
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
        if not self.is_active:
            return False
        
        if current_step is not None:
            return current_step % self.spawn_interval == 0
        else:
            self.step_counter += 1
            return self.step_counter % self.spawn_interval == 0
    
    def reset_step_counter(self) -> None:
        """Reset the internal step counter"""
        self.step_counter = 0
    
    def set_active(self, active: bool) -> None:
        """
        Enable or disable the spawner.
        
        Args:
            active: True to enable, False to disable
        """
        self.is_active = active
    
    def is_spawner_active(self) -> bool:
        """Check if spawner is currently active"""
        return self.is_active
    
    def update_from_config(self, config: Dict[str, Any]) -> None:
        """
        Update spawner parameters from configuration.
        
        Args:
            config: Configuration dictionary containing spawner parameters
        """
        spawner_config = config.get('spawner', {})
        
        if 'x' in spawner_config:
            self.x = spawner_config['x']
        if 'y' in spawner_config:
            self.y = spawner_config['y']
        if 'spawn_count' in spawner_config:
            self.set_spawn_count(spawner_config['spawn_count'])
        if 'spawn_interval' in spawner_config:
            self.set_spawn_interval(spawner_config['spawn_interval'])
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get spawner configuration as dictionary.
        
        Returns:
            Dictionary with spawner configuration
        """
        return {
            'x': self.x,
            'y': self.y,
            'spawn_count': self.spawn_count,
            'spawn_interval': self.spawn_interval
        }
    
    def get_next_spawn_steps(self) -> int:
        """
        Get number of steps until next spawn.
        
        Returns:
            Steps remaining until next spawn
        """
        if not self.is_active:
            return -1  # Inactive
        
        return self.spawn_interval - (self.step_counter % self.spawn_interval)
    
    def force_spawn(self) -> bool:
        """
        Force immediate spawning (resets counter).
        
        Returns:
            True (spawning should occur)
        """
        if not self.is_active:
            return False
        
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
            'is_active': self.is_active,
            'step_counter': self.step_counter,
            'next_spawn_in': self.get_next_spawn_steps()
        }
