# Mondrian Map Core Module
from .core import GridSystem, Block, Line, Corner, Colors, blank_canvas
from .data_processing import (
    get_points, get_areas, get_colors, get_IDs, 
    load_pathway_info, load_dataset, get_mondrian_color_description
)

# Visualization module requires plotly - import only when needed
# from .visualization import create_authentic_mondrian_map, create_canvas_grid, create_color_legend

__version__ = "1.0.0"
__all__ = [
    'GridSystem', 'Block', 'Line', 'Corner', 'Colors', 'blank_canvas',
    'get_points', 'get_areas', 'get_colors', 'get_IDs',
    'load_pathway_info', 'load_dataset', 'get_mondrian_color_description'
] 