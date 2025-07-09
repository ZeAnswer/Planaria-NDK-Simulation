"""
Visualization manager for the mask painter application.
Handles all pyqtgraph visualization components and updates.
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph import ColorMap
from typing import Dict, Any, List, Tuple, Optional


class VisualizationManager:
    """Manages all visualization components for the mask painter"""
    
    def __init__(self, plot_widget: pg.PlotWidget, config: Dict[str, Any]):
        """
        Initialize the visualization manager.
        
        Args:
            plot_widget: PyQtGraph plot widget
            config: Configuration dictionary
        """
        self.plot = plot_widget
        self.config = config
        
        # Visualization items
        self.ellipse_item = None
        self.mask_image_item = None
        self.particle_scatter = None
        self.spawner_scatter = None
        self.divider_lines = []
        self.divider_labels = []
        
        # Color maps
        self.colormap = self._create_colormap()
        
        # Setup plot
        self.setup_plot()
    
    def setup_plot(self):
        """Setup the plot widget properties"""
        self.plot.setAspectLocked(True)
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel('left', 'Y')
        self.plot.setLabel('bottom', 'X')
        self.plot.setTitle('Planaria Particle Simulation')
        
        # Set background color
        self.plot.setBackground('white')
    
    def _create_colormap(self) -> ColorMap:
        """Create color map for mask visualization"""
        colors = [
            (0, 0, 0, 0),      # Transparent for zero values
            (0, 0, 255, 100),  # Blue for low values
            (0, 255, 0, 150),  # Green for medium values
            (255, 255, 0, 200), # Yellow for high values
            (255, 0, 0, 255)   # Red for highest values
        ]
        positions = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        return ColorMap(pos=positions, color=colors)
    
    def create_ellipse_visualization(self, center_x: float, center_y: float, 
                                   radius_x: float, radius_y: float) -> None:
        """
        Create or update ellipse visualization.
        
        Args:
            center_x: Ellipse center X coordinate
            center_y: Ellipse center Y coordinate
            radius_x: Ellipse X radius
            radius_y: Ellipse Y radius
        """
        # Remove existing ellipse
        if self.ellipse_item:
            self.plot.removeItem(self.ellipse_item)
        
        # Get ellipse configuration
        ellipse_config = self.config.get('ellipse', {})
        color = ellipse_config.get('color', '#4CAF50')
        line_width = ellipse_config.get('line_width', 3)
        
        # Create ellipse
        ellipse = pg.EllipseROI(
            pos=[center_x - radius_x, center_y - radius_y],
            size=[2 * radius_x, 2 * radius_y],
            pen=pg.mkPen(color=color, width=line_width),
            movable=False,
            resizable=False
        )
        
        self.ellipse_item = ellipse
        self.plot.addItem(ellipse)
        
        # Set view range with padding
        system_config = self.config.get('system', {})
        view_padding = system_config.get('view_padding', 30)
        
        self.plot.setRange(
            xRange=[center_x - radius_x - view_padding, center_x + radius_x + view_padding],
            yRange=[center_y - radius_y - view_padding, center_y + radius_y + view_padding]
        )
    
    def create_mask_visualization(self, mask_data: np.ndarray, 
                                grid_bounds: Tuple[float, float, float, float]) -> None:
        """
        Create or update mask visualization.
        
        Args:
            mask_data: 2D numpy array with mask data
            grid_bounds: (x_min, x_max, y_min, y_max) of the grid
        """
        if mask_data.size == 0:
            return
        
        # Remove existing mask image
        if self.mask_image_item:
            self.plot.removeItem(self.mask_image_item)
        
        x_min, x_max, y_min, y_max = grid_bounds
        
        # Create image item
        self.mask_image_item = pg.ImageItem()
        
        # Set the data and position
        self.mask_image_item.setImage(mask_data, levels=(0, 1))
        self.mask_image_item.setColorMap(self.colormap)
        
        # Set position and scale
        self.mask_image_item.setRect(x_min, y_min, x_max - x_min, y_max - y_min)
        
        # Add to plot (behind other items)
        self.plot.addItem(self.mask_image_item)
    
    def create_particle_visualization(self) -> None:
        """Create particle scatter plot"""
        if self.particle_scatter:
            self.plot.removeItem(self.particle_scatter)
        
        self.particle_scatter = pg.ScatterPlotItem(
            size=6,
            pen=pg.mkPen(color='red', width=2),
            brush=pg.mkBrush(color='red'),
            symbol='o'
        )
        
        self.plot.addItem(self.particle_scatter)
    
    def create_spawner_visualization(self) -> None:
        """Create spawner visualization"""
        if self.spawner_scatter:
            self.plot.removeItem(self.spawner_scatter)
        
        self.spawner_scatter = pg.ScatterPlotItem(
            size=15,
            pen=pg.mkPen(color='blue', width=3),
            brush=pg.mkBrush(color='lightblue'),
            symbol='s'  # Square symbol
        )
        
        self.plot.addItem(self.spawner_scatter)
    
    def create_divider_visualization(self, dividers: List[Dict[str, Any]], 
                                   ellipse_bounds: Tuple[float, float, float, float]) -> None:
        """
        Create or update divider visualization.
        
        Args:
            dividers: List of divider configuration dictionaries
            ellipse_bounds: (center_x, center_y, radius_x, radius_y) of ellipse
        """
        # Clear existing divider visualizations
        self.clear_divider_visualization()
        
        center_x, center_y, radius_x, radius_y = ellipse_bounds
        y_min = center_y - radius_y
        y_max = center_y + radius_y
        
        for divider in dividers:
            x = divider.get('x', 0)
            color = divider.get('color', '#FF5722')
            name = divider.get('name', 'Divider')
            probability = divider.get('probability', 0.1)
            
            # Create vertical line
            line = pg.PlotCurveItem(
                x=[x, x], 
                y=[y_min, y_max],
                pen=pg.mkPen(color=color, width=3)
            )
            self.plot.addItem(line)
            self.divider_lines.append(line)
            
            # Create label showing name and probability
            label_text = f"{name}: {probability:.2f}"
            label = pg.TextItem(
                text=label_text,
                color=color,
                fill=(255, 255, 255, 150)
            )
            label.setPos(x + 5, center_y + radius_y - 10)
            self.plot.addItem(label)
            self.divider_labels.append(label)
            
            # Create region coloring (optional - could be added later)
            # This would color the region to the right of each divider
    
    def clear_divider_visualization(self) -> None:
        """Clear all divider visualization items"""
        for line in self.divider_lines:
            self.plot.removeItem(line)
        for label in self.divider_labels:
            self.plot.removeItem(label)
        
        self.divider_lines.clear()
        self.divider_labels.clear()
    
    def update_mask_display(self, mask_data: np.ndarray, 
                          grid_bounds: Tuple[float, float, float, float]) -> None:
        """
        Update mask visualization with new data.
        
        Args:
            mask_data: Updated mask data
            grid_bounds: Grid bounds
        """
        if self.mask_image_item and mask_data.size > 0:
            self.mask_image_item.setImage(mask_data, levels=(0, 1))
        else:
            self.create_mask_visualization(mask_data, grid_bounds)
    
    def update_particle_display(self, particle_positions: List[Tuple[float, float]]) -> None:
        """
        Update particle visualization.
        
        Args:
            particle_positions: List of (x, y) particle positions
        """
        if not self.particle_scatter:
            self.create_particle_visualization()
        
        if particle_positions:
            x_coords = [pos[0] for pos in particle_positions]
            y_coords = [pos[1] for pos in particle_positions]
            self.particle_scatter.setData(x=x_coords, y=y_coords)
        else:
            self.particle_scatter.setData(x=[], y=[])
    
    def update_spawner_display(self, spawner_position: Optional[Tuple[float, float]]) -> None:
        """
        Update spawner visualization.
        
        Args:
            spawner_position: (x, y) position of spawner, or None to hide
        """
        if not self.spawner_scatter:
            self.create_spawner_visualization()
        
        if spawner_position:
            x, y = spawner_position
            self.spawner_scatter.setData(x=[x], y=[y])
        else:
            self.spawner_scatter.setData(x=[], y=[])
    
    def update_divider_display(self, dividers: List[Dict[str, Any]], 
                             ellipse_bounds: Tuple[float, float, float, float]) -> None:
        """
        Update divider visualization.
        
        Args:
            dividers: Updated list of divider configurations
            ellipse_bounds: Ellipse bounds
        """
        self.create_divider_visualization(dividers, ellipse_bounds)
    
    def clear_all_visualizations(self) -> None:
        """Clear all visualization items"""
        if self.ellipse_item:
            self.plot.removeItem(self.ellipse_item)
            self.ellipse_item = None
        
        if self.mask_image_item:
            self.plot.removeItem(self.mask_image_item)
            self.mask_image_item = None
        
        if self.particle_scatter:
            self.plot.removeItem(self.particle_scatter)
            self.particle_scatter = None
        
        if self.spawner_scatter:
            self.plot.removeItem(self.spawner_scatter)
            self.spawner_scatter = None
        
        self.clear_divider_visualization()
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration and refresh visualizations if needed.
        
        Args:
            config: New configuration dictionary
        """
        self.config = config
        
        # Check if ellipse parameters changed
        ellipse_config = config.get('ellipse', {})
        center_x = ellipse_config.get('center_x', 150)
        center_y = ellipse_config.get('center_y', 100)
        radius_x = ellipse_config.get('radius_x', 150)
        radius_y = ellipse_config.get('radius_y', 50)
        
        # Update ellipse visualization
        self.create_ellipse_visualization(center_x, center_y, radius_x, radius_y)
        
        # Update divider visualization
        dividers = config.get('dividers', [])
        self.update_divider_display(dividers, (center_x, center_y, radius_x, radius_y))
    
    def get_plot_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get current plot view bounds.
        
        Returns:
            (x_min, x_max, y_min, y_max) of current view
        """
        x_range = self.plot.getViewBox().viewRange()[0]
        y_range = self.plot.getViewBox().viewRange()[1]
        
        return (x_range[0], x_range[1], y_range[0], y_range[1])
    
    def set_plot_range(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        """
        Set plot view range.
        
        Args:
            x_min, x_max: X range
            y_min, y_max: Y range
        """
        self.plot.setRange(xRange=[x_min, x_max], yRange=[y_min, y_max])
    
    def export_plot(self, filename: str) -> bool:
        """
        Export current plot to image file.
        
        Args:
            filename: Output filename
            
        Returns:
            True if export was successful
        """
        try:
            exporter = pg.exporters.ImageExporter(self.plot.plotItem)
            exporter.export(filename)
            return True
        except Exception as e:
            print(f"Error exporting plot: {e}")
            return False
