"""
Configuration management for the mask painter application.
Handles loading, saving, and managing configuration profiles.
"""

import os
import yaml
import copy
from typing import Dict, Any, List, Optional


class ConfigManager:
    """Manages configuration loading, saving, and profile management"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the main configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                self.config = self._get_default_config()
                self.save_config()
            return self.config
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._get_default_config()
            return self.config
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get a specific profile configuration"""
        profiles = self.config.get('profiles', {})
        return profiles.get(profile_name, {})
    
    def save_profile(self, profile_name: str, current_state: Dict[str, Any]) -> bool:
        """Save current state as a profile"""
        try:
            if 'profiles' not in self.config:
                self.config['profiles'] = {}
            
            self.config['profiles'][profile_name] = copy.deepcopy(current_state)
            return self.save_config()
        except Exception as e:
            print(f"Error saving profile {profile_name}: {e}")
            return False
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile names"""
        return list(self.config.get('profiles', {}).keys())
    
    def merge_profile_config(self, profile_name: str) -> Dict[str, Any]:
        """
        Merge a profile with the default profile to get complete configuration.
        
        Args:
            profile_name: Name of the profile to merge
            
        Returns:
            Complete configuration with profile overrides applied
        """
        # Start with default profile
        default_profile = self.get_profile('default')
        if not default_profile:
            return {}
        
        # If requesting default, return it as-is
        if profile_name == 'default':
            return copy.deepcopy(default_profile)
        
        # Get the target profile
        target_profile = self.get_profile(profile_name)
        if not target_profile:
            return copy.deepcopy(default_profile)
        
        # Deep merge target into default
        merged = copy.deepcopy(default_profile)
        self.deep_merge_dicts(merged, target_profile)
        
        return merged
    
    def deep_merge_dicts(self, base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> None:
        """
        Recursively merge override_dict into base_dict.
        
        Args:
            base_dict: Dictionary to merge into (modified in place)
            override_dict: Dictionary with override values
        """
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self.deep_merge_dicts(base_dict[key], value)
            else:
                base_dict[key] = copy.deepcopy(value)
    
    def get_current_profile_name(self) -> str:
        """Get the name of the currently selected profile"""
        return self.config.get('current_profile', 'default')
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Set the current profile"""
        if profile_name in self.get_available_profiles():
            self.config['current_profile'] = profile_name
            return self.save_config()
        return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile (cannot delete 'default')"""
        if profile_name == 'default':
            return False
        
        profiles = self.config.get('profiles', {})
        if profile_name in profiles:
            del profiles[profile_name]
            
            # If this was the current profile, switch to default
            if self.get_current_profile_name() == profile_name:
                self.set_current_profile('default')
            
            return self.save_config()
        return False
    
    def update_mask_info(self, mask_info: Dict[str, Any]) -> bool:
        """Update mask information in config"""
        self.config['mask_info'] = copy.deepcopy(mask_info)
        return self.save_config()
    
    def get_mask_info(self) -> Dict[str, Any]:
        """Get mask information from config"""
        return self.config.get('mask_info', {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            'profiles': {
                'default': {
                    'ellipse': {
                        'center_x': 150,
                        'center_y': 100,
                        'color': '#4CAF50',
                        'line_width': 3,
                        'radius_x': 150,
                        'radius_y': 50
                    },
                    'particles': {
                        'velocity': 10.0,
                        'lifetime': 1000
                    },
                    'spawner': {
                        'x': 150,
                        'y': 100,
                        'spawn_count': 3,
                        'spawn_interval': 5
                    },
                    'catching': {
                        'probability': 0.05,
                        'radius': 3.0,
                        'exposure': 0.2
                    },
                    'step_function': {
                        'decay_rate': 0.02,
                        'saturation_threshold': 0.95,
                        'step_interval': 100
                    },
                    'system': {
                        'count_particles': True,
                        'mask_resolution': 100,
                        'grid_padding': 0,
                        'view_padding': 30
                    },
                    'dividers': [],
                    'ui_ranges': {
                        'velocity_slider': {'min': 1, 'max': 50},
                        'catch_prob_slider': {'min': 1, 'max': 100},
                        'catch_radius_slider': {'min': 1, 'max': 20},
                        'catch_exposure_slider': {'min': 1, 'max': 100},
                        'decay_slider': {'min': 0, 'max': 100},
                        'interval_slider': {'min': 50, 'max': 2000},
                        'spawn_count_slider': {'min': 1, 'max': 10},
                        'spawn_interval_slider': {'min': 1, 'max': 20}
                    }
                }
            },
            'current_profile': 'default',
            'mask_info': {}
        }
