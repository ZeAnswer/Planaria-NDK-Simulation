"""
Particle system for the mask painter application.
Handles individual particles and particle management.
"""

import numpy as np
from typing import List, Tuple, Dict, Any


class Particle:
    """A single particle that moves and paints"""
    
    def __init__(self, x: float, y: float, velocity: float, angle: float = None, movement_mode: str = "diffusion"):
        """
        Initialize a particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            velocity: Movement velocity
            angle: Initial movement angle (random if None)
            movement_mode: Movement mode ("straight" or "diffusion")
        """
        self.x = x
        self.y = y
        self.velocity = velocity
        self.movement_mode = movement_mode  # "straight" or "diffusion"
        
        # Random initial direction if not specified
        if angle is None:
            self.angle = np.random.uniform(0, 2 * np.pi)
        else:
            self.angle = angle
            
        # Velocity components for straight-line movement
        self.vx = velocity * np.cos(self.angle)
        self.vy = velocity * np.sin(self.angle)
        
        self.age = 0  # How many steps this particle has existed
        
    def move(self, dt: float = 1.0) -> None:
        """Move the particle by one time step"""
        if self.movement_mode == "straight":
            # Straight-line movement
            self.x += self.vx * dt
            self.y += self.vy * dt
        elif self.movement_mode == "diffusion":
            # Random movement (diffusion)
            sigma = np.sqrt(2 * self.velocity * dt)
            self.x += np.random.normal(0, sigma)
            self.y += np.random.normal(0, sigma)

        self.age += 1
        
    def reflect_at_boundary(self,
                        center_x: float,
                        center_y: float,
                        radius_x: float,
                        radius_y: float,
                        bounce: float = 0.5) -> None:
        """
        Prevent particle from passing through the ellipse boundary.
        
        Parameters:
        bounce: float in [0,1]
            0.0 → remove only the outward component (slip boundary)
            1.0 → perfect elastic bounce
            intermediate → partial bounce
        """
        # compute offset from ellipse center
        dx = self.x - center_x
        dy = self.y - center_y
        dist_normalized = (dx / radius_x) ** 2 + (dy / radius_y) ** 2

        if dist_normalized >= 1.0:
            # 1) clamp position just inside the boundary
            scale = np.sqrt(1.0 / dist_normalized) * 0.99
            self.x = center_x + dx * scale
            self.y = center_y + dy * scale

            # 2) compute outward normal at boundary
            nx = 2 * dx / (radius_x ** 2)
            ny = 2 * dy / (radius_y ** 2)
            norm = np.hypot(nx, ny)
            if norm > 0:
                nx /= norm
                ny /= norm

                # 3) project velocity onto normal
                dot = self.vx * nx + self.vy * ny
                if dot > 0:
                    # v_normal = dot * n
                    # remove v_normal and then add back (-bounce * v_normal):
                    # v_new = v - (1 + bounce)*v_normal
                    corr = (1.0 + bounce) * dot
                    self.vx -= corr * nx
                    self.vy -= corr * ny
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position as tuple"""
        return (self.x, self.y)
    
    def is_expired(self, max_lifetime: int) -> bool:
        """Check if particle has exceeded its lifetime"""
        return self.age >= max_lifetime


class ParticleManager:
    """Manages a collection of particles"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the particle manager.
        
        Args:
            config: Configuration dictionary containing particle parameters
        """
        self.particles: List[Particle] = []
        self.config = config
        self.max_lifetime = config.get('particles', {}).get('lifetime', 1000)
        
        # Ellipse boundary parameters
        ellipse_config = config.get('ellipse', {})
        self.center_x = ellipse_config.get('center_x', 150)
        self.center_y = ellipse_config.get('center_y', 100)
        self.radius_x = ellipse_config.get('radius_x', 150)
        self.radius_y = ellipse_config.get('radius_y', 50)
    
    def spawn_particle(self, x: float, y: float, velocity: float = None, 
                      angle: float = None) -> Particle:
        """
        Spawn a new particle at the given position.
        
        Args:
            x: Spawn x position
            y: Spawn y position
            velocity: Particle velocity (uses config default if None)
            angle: Initial angle (random if None)
            
        Returns:
            The newly created particle
        """
        if velocity is None:
            velocity = self.config.get('particles', {}).get('velocity', 10.0)
        
        particle = Particle(x, y, velocity, angle)
        self.particles.append(particle)
        return particle
    
    def spawn_multiple_particles(self, x: float, y: float, count: int, 
                                velocity: float = None) -> List[Particle]:
        """
        Spawn multiple particles at the same position with random angles.
        
        Args:
            x: Spawn x position
            y: Spawn y position
            count: Number of particles to spawn
            velocity: Particle velocity (uses config default if None)
            
        Returns:
            List of newly created particles
        """
        new_particles = []
        for _ in range(count):
            particle = self.spawn_particle(x, y, velocity)
            new_particles.append(particle)
        return new_particles
    
    def move_all_particles(self, dt: float = 1.0) -> None:
        """Move all particles and handle boundary reflections"""
        for particle in self.particles:
            particle.move(dt)
            particle.reflect_at_boundary(
                self.center_x, self.center_y, 
                self.radius_x, self.radius_y
            )
    
    def remove_expired_particles(self) -> int:
        """
        Remove particles that have exceeded their lifetime.
        
        Returns:
            Number of particles removed
        """
        initial_count = len(self.particles)
        self.particles = [p for p in self.particles if not p.is_expired(self.max_lifetime)]
        return initial_count - len(self.particles)
    
    def remove_particle(self, particle: Particle) -> bool:
        """
        Remove a specific particle.
        
        Args:
            particle: Particle to remove
            
        Returns:
            True if particle was found and removed
        """
        if particle in self.particles:
            self.particles.remove(particle)
            return True
        return False
    
    def clear_all_particles(self) -> int:
        """
        Remove all particles.
        
        Returns:
            Number of particles that were removed
        """
        count = len(self.particles)
        self.particles.clear()
        return count
    
    def get_particle_positions(self) -> List[Tuple[float, float]]:
        """Get positions of all particles for visualization"""
        return [particle.get_position() for particle in self.particles]
    
    def get_particle_count(self) -> int:
        """Get current number of particles"""
        return len(self.particles)
    
    def get_particles(self) -> List[Particle]:
        """Get list of all particles"""
        return self.particles.copy()
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration parameters"""
        self.config = config
        self.max_lifetime = config.get('particles', {}).get('lifetime', 1000)
        
        # Update ellipse boundary parameters
        ellipse_config = config.get('ellipse', {})
        self.center_x = ellipse_config.get('center_x', 150)
        self.center_y = ellipse_config.get('center_y', 100)
        self.radius_x = ellipse_config.get('radius_x', 150)
        self.radius_y = ellipse_config.get('radius_y', 50)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about current particles"""
        if not self.particles:
            return {
                'count': 0,
                'average_age': 0,
                'oldest_particle': 0,
                'average_velocity': 0
            }
        
        ages = [p.age for p in self.particles]
        velocities = [p.velocity for p in self.particles]
        
        return {
            'count': len(self.particles),
            'average_age': np.mean(ages),
            'oldest_particle': max(ages),
            'average_velocity': np.mean(velocities)
        }