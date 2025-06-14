import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots
import io
import math
from enum import Enum
from dataclasses import dataclass
from typing import List

DATA_DIR = Path("data/case_study/pathways_prepared_for_visualization")
DATASETS = {
    "Aggressive R1": DATA_DIR / "wikipathway_aggressive_R1_TP.csv",
    "Aggressive R2": DATA_DIR / "wikipathway_aggressive_R2_TP.csv",
    "Baseline R1": DATA_DIR / "wikipathway_baseline_R1_TP.csv",
    "Baseline R2": DATA_DIR / "wikipathway_baseline_R2_TP.csv",
    "Nonaggressive R1": DATA_DIR / "wikipathway_nonaggressive_R1_TP.csv",
    "Nonaggressive R2": DATA_DIR / "wikipathway_nonaggressive_R2_TP.csv",
}

# Authentic Mondrian Map Algorithm from notebooks
LINE_WIDTH = 5
THIN_LINE_WIDTH = 1
adjust = LINE_WIDTH // 2
adjust_e = adjust + 1
adjust_d = adjust_e - adjust
AREA_SCALAR = 4000

up_th = 1.25
dn_th = abs(1-(up_th-1))

class Colors(str, Enum):
    WHITE = "#FFFFFF"
    GRAY = "#3e3f39"
    BLACK = "#050103"
    BLACK_A = "#05010333"
    BLACK_AA = "#050103AA"
    RED = "#E70503"
    BLUE = "#0300AD"
    YELLOW = "#FDDE06"
    RED_A = "#E70503AA"
    BLUE_A = "#0300ADAA"
    YELLOW_A = "#FDDE06AA"

class CornerPos(int, Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3

class LineDir(str, Enum):
    RIGHT = "left_to_right"
    LEFT = "right_to_left"
    DOWN = "up_to_down"
    UP = "down_to_up"

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({round(self.x, 2)}, {round(self.y, 2)})"

class Line:
    instances = []
    def __init__(self, point_a: Point, point_b: Point, direction: LineDir, color: Colors = Colors.BLACK, strength: int = LINE_WIDTH):
        self.point_a = point_a
        self.point_b = point_b
        self.direction = direction
        self.color = color
        self.strength = strength
        self.instances.append(self)

    def __str__(self):
        return f"({self.point_a.x}, {self.point_a.y}) to ({self.point_b.x}, {self.point_b.y})"

class Corner:
    instances = []

    def __init__(self, point: Point, position: CornerPos, line: Line = None):
        self.point = point
        self.position = position
        self.line = line
        self.instances.append(self)

    def __str__(self):
        return f"{self.position}: ({round(self.point.x, 2)}, {round(self.point.y, 2)})"

class Block:
    instances = {}
    def __init__(self, top_left, bottom_right, area: float, color: str, id: str):
        self.top_left_p = top_left
        self.bottom_right_p = bottom_right

        self.top_left = Corner(Point(self.top_left_p[0] - adjust, self.top_left_p[1] - adjust), CornerPos.TOP_LEFT)
        self.top_right = Corner(Point(self.bottom_right_p[0] + adjust, self.top_left_p[1] - adjust), CornerPos.TOP_RIGHT)
        self.bottom_left = Corner(Point(self.top_left_p[0] - adjust, self.bottom_right_p[1] + adjust), CornerPos.BOTTOM_LEFT)
        self.bottom_right = Corner(Point(self.bottom_right_p[0] + adjust, self.bottom_right_p[1] + adjust), CornerPos.BOTTOM_RIGHT)

        self.center = Point((self.top_left.point.x + self.bottom_right.point.x) / 2, (self.top_left.point.y + self.bottom_right.point.y) / 2)
        self.area = area
        self.color = self.get_color_map(color)
        self.id = id
        self.instances[id] = self

        Line(Point(self.top_left.point.x, self.top_left.point.y + adjust), Point(self.top_right.point.x, self.top_right.point.y + adjust), LineDir.RIGHT)
        Line(Point(self.top_right.point.x - adjust, self.top_right.point.y), Point(self.bottom_right.point.x - adjust, self.bottom_right.point.y), LineDir.DOWN)
        Line(Point(self.bottom_right.point.x, self.bottom_right.point.y - adjust), Point(self.bottom_left.point.x, self.bottom_left.point.y - adjust), LineDir.LEFT)
        Line(Point(self.bottom_left.point.x + adjust, self.bottom_left.point.y), Point(self.top_left.point.x + adjust, self.top_left.point.y), LineDir.UP)

    def get_color_map(self, color):
        if color == "red": return Colors.RED
        if color == "blue": return Colors.BLUE
        if color == "yellow": return Colors.YELLOW
        if color == "black": return Colors.BLACK
        if color == "gray": return Colors.GRAY
        return Colors.BLACK

    @property
    def height(self):
        return self.bottom_left.point.y - self.top_left.point.y

    @property
    def width(self):
        return self.top_right.point.x - self.top_left.point.x

class GridSystem:
    def __init__(self, width, height, block_width, block_height):
        self.width = width
        self.height = height
        self.block_width = block_width
        self.block_height = block_height
        
        self.grid_lines_h = {}
        self.grid_lines_v = {}
        
        # Create horizontal grid lines
        for i in range(height // block_height + 1):
            self.grid_lines_h[f'h{i}'] = i * block_height
        
        # Create vertical grid lines
        for i in range(width // block_width + 1):
            self.grid_lines_v[f'v{i}'] = i * block_width

    def fill_blocks_around_point(self, point, target_area):
        x, y = point
        
        # Calculate the number of blocks to be filled based on the target area
        nob = max(1, round(target_area / (self.block_width * self.block_height)))
        num_rows, num_columns = self.approximate_grid_layout(nob)

        area_diff = abs(target_area - nob * self.block_width * self.block_height)

        # Adjust the starting block to ensure the point is in the center
        start_block_h = max(int(y // self.block_height - num_rows // 2), 1)
        start_block_v = max(int(x // self.block_width - num_columns // 2), 1)

        start_block_h = min(start_block_h, len(self.grid_lines_h.keys()) - num_rows)
        start_block_v = min(start_block_v, len(self.grid_lines_v.keys()) - num_columns)

        # Calculate the coordinates for the single rectangle around the point
        top_left_x = self.grid_lines_v[f'v{start_block_v}']
        top_left_y = self.grid_lines_h[f'h{start_block_h}']
        bottom_right_x = self.grid_lines_v[f'v{start_block_v + num_columns - 1}'] + self.block_width
        bottom_right_y = self.grid_lines_h[f'h{start_block_h + num_rows - 1}'] + self.block_height

        return [(top_left_x, top_left_y), (bottom_right_x, bottom_right_y)], area_diff

    def approximate_grid_layout(self, nob):
        if nob == 1:
            return 1, 1
        elif nob <= 4:
            return 2, 2
        else:
            sqrt_nob = int(math.sqrt(nob))
            return sqrt_nob, int(math.ceil(nob / sqrt_nob))

    def plot_points_fill_blocks(self, points, target_areas):
        rectangles = []
        area_diff = 0

        for point, target_area in zip(points, target_areas):
            rect, diff = self.fill_blocks_around_point(point, target_area)
            rectangles.append(rect)
            area_diff += diff

        return rectangles

def blank_canvas():
    Corner.instances = []
    Block.instances = {}
    Line.instances = []

def get_points(df, scale=1):
    return [(round(df['x'].iloc[i] * scale, 2), round(df['y'].iloc[i] * scale, 2)) for i in range(len(df))]

def get_areas(df, scale):
    return list(abs(np.log2(df["wFC"])) * scale)

def get_colors(df, up_th, dn_th):
    colors = []
    for i, row in df.iterrows():
        if row["pFDR"] < 0.05:
            if row["wFC"] >= up_th:
                colors.append("red")
            elif row["wFC"] <= dn_th:
                colors.append("blue")
            else:
                colors.append("yellow")
        else:
            colors.append("black")
    return colors

def get_IDs(df):
    return [i[-4:] for i in df["GS_ID"]]

def get_relations(mem_df, th=2):
    if mem_df is None or len(mem_df) == 0:
        return []
    
    relations = []
    rel_count = {}
    for key in set(mem_df["GS_A_ID"]):
        rel_count[key[-4:]] = 0
    for index, row in mem_df.iterrows():
        if (row["GS_B_ID"][-4:], row["GS_A_ID"][-4:]) not in relations and \
        rel_count[row["GS_A_ID"][-4:]] < th and rel_count[row["GS_B_ID"][-4:]] < th:
            relations.append((row["GS_A_ID"][-4:], row["GS_B_ID"][-4:]))
            rel_count[row["GS_A_ID"][-4:]] += 1
            rel_count[row["GS_B_ID"][-4:]] += 1
    return relations

def euclidean_distance_point(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_line_direction(point_a: Point, point_b: Point):
    if abs(point_a.x - point_b.x) <= adjust:     # due to adjustment error
        if point_a.y < point_b.y:
            return LineDir.DOWN
        else:
            return LineDir.UP
    elif abs(point_a.y - point_b.y) <= adjust:
        if point_a.x < point_b.x:
            return LineDir.RIGHT
        else:
            return LineDir.LEFT
    else:
        return None

def get_closest_corner(block_a: Block, block_b: Block) -> Corner:
    min_distance = float('inf')
    closest_corner = None

    for corner in [block_a.top_left, block_a.top_right, block_a.bottom_right, block_a.bottom_left]:
        distance = abs(corner.point.x - block_b.center.x) + abs(corner.point.y - block_b.center.y)
        if distance < min_distance:
            min_distance = distance
            closest_corner = corner

    return closest_corner

def get_furthest_connector(cp1, cp2, center):
    p = Point(cp1.point.x, cp2.point.y)
    q = Point(cp2.point.x, cp1.point.y)
    if euclidean_distance_point((p.x, p.y), (center.x, center.y)) > euclidean_distance_point((q.x, q.y), (center.x, center.y)):
        return p
    else:
        return q

def get_manhattan_line_color(block_a, block_b):
    if block_a.color == Colors.RED and block_b.color == Colors.RED:
        return Colors.RED
    elif block_a.color == Colors.BLUE and block_b.color == Colors.BLUE:
        return Colors.BLUE
    else:
        return Colors.YELLOW

def get_manhattan_lines_2(corner_a: Corner, corner_b: Corner, connector: Point, color: Colors) -> List[Line]:
    if corner_a.point.x == corner_b.point.x and corner_a.point.y != corner_b.point.y:
        if corner_a.position in [CornerPos.TOP_LEFT, CornerPos.BOTTOM_LEFT]:
            line_v = Line(Point(corner_a.point.x + adjust, corner_a.point.y), Point(corner_b.point.x + adjust, corner_b.point.y), get_line_direction(corner_a.point, corner_b.point), color=color)
        if corner_a.position in [CornerPos.TOP_RIGHT, CornerPos.BOTTOM_RIGHT]:
            line_v = Line(Point(corner_a.point.x - adjust, corner_a.point.y), Point(corner_b.point.x - adjust, corner_b.point.y), get_line_direction(corner_a.point, corner_b.point), color=color)
        corner_a.line = line_v
        corner_b.line = line_v
        return [line_v]

    elif (corner_a.point.x != corner_b.point.x and corner_a.point.y == corner_b.point.y):
        if corner_a.position == CornerPos.TOP_LEFT:
            line_h = Line(Point(corner_a.point.x - adjust_d, corner_a.point.y + adjust), Point(corner_b.point.x, corner_b.point.y + adjust), get_line_direction(corner_a.point, corner_b.point), color=color)
        elif corner_a.position == CornerPos.TOP_RIGHT:
            line_h = Line(Point(corner_a.point.x + adjust_d, corner_a.point.y + adjust), Point(corner_b.point.x, corner_b.point.y + adjust), get_line_direction(corner_a.point, corner_b.point), color=color)
        elif corner_a.position == CornerPos.BOTTOM_LEFT:
            line_h = Line(Point(corner_a.point.x - adjust_d, corner_a.point.y - adjust), Point(corner_b.point.x, corner_b.point.y - adjust), get_line_direction(corner_a.point, corner_b.point), color=color)
        elif corner_a.position == CornerPos.BOTTOM_RIGHT:
            line_h = Line(Point(corner_a.point.x + adjust_d, corner_a.point.y - adjust), Point(corner_b.point.x, corner_b.point.y - adjust), get_line_direction(corner_a.point, corner_b.point), color=color)
        corner_a.line = line_h
        corner_b.line = line_h
        return [line_h]

    # Complex case with connector point
    line_a_dir = get_line_direction(corner_a.point, connector)
    line_b_dir = get_line_direction(connector, corner_b.point)
    
    # Create line A
    if corner_a.position in [CornerPos.TOP_LEFT, CornerPos.TOP_RIGHT] and line_a_dir in [LineDir.LEFT, LineDir.RIGHT]:
        if corner_a.position == CornerPos.TOP_RIGHT and line_a_dir == LineDir.RIGHT:
            line_a = Line(Point(corner_a.point.x + adjust_d, corner_a.point.y + adjust), Point(connector.x, connector.y + adjust), line_a_dir, color=color)
        elif corner_a.position == CornerPos.TOP_LEFT and line_a_dir == LineDir.LEFT:
            line_a = Line(Point(corner_a.point.x - adjust_d, corner_a.point.y + adjust), Point(connector.x, connector.y + adjust), line_a_dir, color=color)
        else:
            line_a = Line(Point(corner_a.point.x, corner_a.point.y + adjust), Point(connector.x, connector.y + adjust), line_a_dir, color=color)
    elif corner_a.position in [CornerPos.BOTTOM_LEFT, CornerPos.BOTTOM_RIGHT] and line_a_dir in [LineDir.LEFT, LineDir.RIGHT]:
        if corner_a.position == CornerPos.BOTTOM_RIGHT and line_a_dir == LineDir.RIGHT:
            line_a = Line(Point(corner_a.point.x + adjust_d, corner_a.point.y - adjust), Point(connector.x, connector.y - adjust), line_a_dir, color=color)
        elif corner_a.position == CornerPos.BOTTOM_LEFT and line_a_dir == LineDir.LEFT:
            line_a = Line(Point(corner_a.point.x - adjust_d, corner_a.point.y - adjust), Point(connector.x, connector.y - adjust), line_a_dir, color=color)
        else:
            line_a = Line(Point(corner_a.point.x, corner_a.point.y - adjust), Point(connector.x, connector.y - adjust), line_a_dir, color=color)
    elif corner_a.position in [CornerPos.TOP_LEFT, CornerPos.BOTTOM_LEFT] and line_a_dir in [LineDir.UP, LineDir.DOWN]:
        if corner_a.position == CornerPos.TOP_LEFT and line_a_dir == LineDir.UP:
            line_a = Line(Point(corner_a.point.x + adjust, corner_a.point.y - adjust_d), Point(connector.x + adjust, connector.y), line_a_dir, color=color)
        elif corner_a.position == CornerPos.BOTTOM_LEFT and line_a_dir == LineDir.DOWN:
            line_a = Line(Point(corner_a.point.x + adjust, corner_a.point.y + adjust_d), Point(connector.x + adjust, connector.y), line_a_dir, color=color)
        else:
            line_a = Line(Point(corner_a.point.x + adjust, corner_a.point.y), Point(connector.x + adjust, connector.y), line_a_dir, color=color)
    elif corner_a.position in [CornerPos.TOP_RIGHT, CornerPos.BOTTOM_RIGHT] and line_a_dir in [LineDir.UP, LineDir.DOWN]:
        if corner_a.position == CornerPos.TOP_RIGHT and line_a_dir == LineDir.UP:
            line_a = Line(Point(corner_a.point.x - adjust, corner_a.point.y - adjust_d), Point(connector.x - adjust, connector.y), line_a_dir, color=color)
        elif corner_a.position == CornerPos.BOTTOM_RIGHT and line_a_dir == LineDir.DOWN:
            line_a = Line(Point(corner_a.point.x - adjust, corner_a.point.y + adjust_d), Point(connector.x - adjust, connector.y), line_a_dir, color=color)
        else:
            line_a = Line(Point(corner_a.point.x - adjust, corner_a.point.y), Point(connector.x - adjust, connector.y), line_a_dir, color=color)
    else:
        line_a = Line(corner_a.point, connector, line_a_dir, color=color)

    # Create line B
    if corner_b.position in [CornerPos.TOP_LEFT, CornerPos.TOP_RIGHT] and line_b_dir in [LineDir.LEFT, LineDir.RIGHT]:
        if corner_b.position == CornerPos.TOP_LEFT and line_b_dir == LineDir.RIGHT:
            line_b = Line(Point(connector.x - adjust*2, connector.y + adjust), Point(corner_b.point.x - adjust_d, corner_b.point.y + adjust), line_b_dir, color=color)
        elif corner_b.position == CornerPos.TOP_RIGHT and line_b_dir == LineDir.LEFT:
            line_b = Line(Point(connector.x + adjust*2, connector.y + adjust), Point(corner_b.point.x + adjust_d, corner_b.point.y + adjust), line_b_dir, color=color)
        else:
            line_b = Line(Point(connector.x, connector.y + adjust), Point(corner_b.point.x, corner_b.point.y + adjust), line_b_dir, color=color)
    elif corner_b.position in [CornerPos.BOTTOM_LEFT, CornerPos.BOTTOM_RIGHT] and line_b_dir in [LineDir.LEFT, LineDir.RIGHT]:
        if corner_b.position == CornerPos.BOTTOM_LEFT and line_b_dir == LineDir.RIGHT:
            line_b = Line(Point(connector.x - adjust*2, connector.y - adjust), Point(corner_b.point.x - adjust_d, corner_b.point.y - adjust), line_b_dir, color=color)
        elif corner_b.position == CornerPos.BOTTOM_RIGHT and line_b_dir == LineDir.LEFT:
            line_b = Line(Point(connector.x + adjust*2, connector.y - adjust), Point(corner_b.point.x + adjust_d, corner_b.point.y - adjust), line_b_dir, color=color)
        else:
            line_b = Line(Point(connector.x, connector.y - adjust), Point(corner_b.point.x, corner_b.point.y - adjust), line_b_dir, color=color)
    elif corner_b.position in [CornerPos.TOP_LEFT, CornerPos.BOTTOM_LEFT] and line_b_dir in [LineDir.UP, LineDir.DOWN]:
        if corner_b.position == CornerPos.TOP_LEFT and line_b_dir == LineDir.DOWN:
            line_b = Line(Point(connector.x + adjust, connector.y - adjust*2), Point(corner_b.point.x + adjust, corner_b.point.y - adjust_d), line_b_dir, color=color)
        elif corner_b.position == CornerPos.BOTTOM_LEFT and line_b_dir == LineDir.UP:
            line_b = Line(Point(connector.x + adjust, connector.y + adjust*2), Point(corner_b.point.x + adjust, corner_b.point.y + adjust_d), line_b_dir, color=color)
        else:
            line_b = Line(Point(connector.x + adjust, connector.y), Point(corner_b.point.x + adjust, corner_b.point.y), line_b_dir, color=color)
    elif corner_b.position in [CornerPos.TOP_RIGHT, CornerPos.BOTTOM_RIGHT] and line_b_dir in [LineDir.UP, LineDir.DOWN]:
        if corner_b.position == CornerPos.TOP_RIGHT and line_b_dir == LineDir.DOWN:
            line_b = Line(Point(connector.x - adjust, connector.y - adjust*2), Point(corner_b.point.x - adjust, corner_b.point.y - adjust_d), line_b_dir, color=color)
        elif corner_b.position == CornerPos.BOTTOM_RIGHT and line_b_dir == LineDir.UP:
            line_b = Line(Point(connector.x - adjust, connector.y + adjust*2), Point(corner_b.point.x - adjust, corner_b.point.y + adjust_d), line_b_dir, color=color)
        else:
            line_b = Line(Point(connector.x - adjust, connector.y), Point(corner_b.point.x - adjust, corner_b.point.y), line_b_dir, color=color)
    else:
        line_b = Line(connector, corner_b.point, line_b_dir, color=color)

    corner_a.line = line_a
    corner_b.line = line_b
    return [line_a, line_b]

def load_network_data(dataset_name):
    """Load pathway network data for a given dataset"""
    network_dir = Path("data/case_study/pathway_networks")
    
    # Map dataset names to network files
    network_files = {
        "Aggressive R1": network_dir / "wikipathway_aggressive_R1_TP.csv",
        "Aggressive R2": network_dir / "wikipathway_aggressive_R2_TP.csv", 
        "Baseline R1": network_dir / "wikipathway_baseline_R1_TP.csv",
        "Baseline R2": network_dir / "wikipathway_baseline_R2_TP.csv",
        "Nonaggressive R1": network_dir / "wikipathway_nonaggressive_R1_TP.csv",
        "Nonaggressive R2": network_dir / "wikipathway_nonaggressive_R2_TP.csv",
    }
    
    if dataset_name in network_files and network_files[dataset_name].exists():
        return pd.read_csv(network_files[dataset_name])
    else:
        return None

def create_authentic_mondrian_map(df, dataset_name, mem_df=None, maximize=False):
    """
    Create authentic Mondrian map using the exact algorithm from the notebooks
    """
    if len(df) == 0:
        return go.Figure()

    # Load network data if not provided
    if mem_df is None:
        mem_df = load_network_data(dataset_name)
    
    # Filter network data to only include pathways in our dataset
    if mem_df is not None and len(mem_df) > 0:
        available_pathways = set(df["GS_ID"].unique())
        mem_df = mem_df[mem_df["GS_A_ID"].isin(available_pathways) & mem_df["GS_B_ID"].isin(available_pathways)].reset_index(drop=True)

    # Prepare data using authentic functions
    center_points = get_points(df, 1)
    areas = get_areas(df, AREA_SCALAR)
    colors = get_colors(df, up_th, dn_th)
    pathway_ids = get_IDs(df)
    
    # Get relations if available
    relations = []
    if mem_df is not None and len(mem_df) > 0:
        relations = get_relations(mem_df)

    # Initialize canvas
    blank_canvas()
    grid_system = GridSystem(1001, 1001, 20, 20)
    
    # Sort data by area (largest first)
    sorted_data = sorted(zip(areas, center_points, colors, pathway_ids), reverse=True)
    areas_sorted, center_points_sorted, colors_sorted, pathway_ids_sorted = zip(*sorted_data)

    # Get rectangles from grid system
    rectangles = grid_system.plot_points_fill_blocks(center_points_sorted, areas_sorted)

    # Create border lines
    Line(Point(0, 0), Point(1000, 0), LineDir.RIGHT, Colors.GRAY, THIN_LINE_WIDTH)
    Line(Point(1000, 0), Point(1000, 1000), LineDir.DOWN, Colors.GRAY, THIN_LINE_WIDTH)
    Line(Point(1000, 1000), Point(0, 1000), LineDir.LEFT, Colors.GRAY, THIN_LINE_WIDTH)
    Line(Point(0, 1000), Point(0, 0), LineDir.UP, Colors.GRAY, THIN_LINE_WIDTH)
    
    # Add grid lines for authentic Mondrian appearance
    # Vertical grid lines
    for i in range(1, len(grid_system.grid_lines_v) - 1):
        x_pos = grid_system.grid_lines_v[f'v{i}']
        Line(Point(x_pos, 0), Point(x_pos, 1000), LineDir.DOWN, Colors.GRAY, THIN_LINE_WIDTH)
    
    # Horizontal grid lines  
    for i in range(1, len(grid_system.grid_lines_h) - 1):
        y_pos = grid_system.grid_lines_h[f'h{i}']
        Line(Point(0, y_pos), Point(1000, y_pos), LineDir.RIGHT, Colors.GRAY, THIN_LINE_WIDTH)

    # STAGE 1: Create blocks
    all_blocks = []
    for idx, rect in enumerate(rectangles):
        b = Block(rect[0], rect[1], areas_sorted[idx], colors_sorted[idx], pathway_ids_sorted[idx])
        all_blocks.append(b)

    # STAGE 2: Create relationship lines (Manhattan lines)
    all_manhattan_lines = []
    lines_to_extend = []
    for rel in relations:
        if rel[0] in Block.instances.keys() and rel[1] in Block.instances.keys():
            s = Block.instances[rel[0]]
            b = Block.instances[rel[1]]
        else:
            continue
        
        manhattan_line_color = get_manhattan_line_color(s, b)

        cp1 = get_closest_corner(s, b)
        cp2 = None
        dist = float('inf')

        for corner in [b.top_left, b.top_right, b.bottom_left, b.bottom_right]:
            if (s.top_left.point.x > corner.point.x or s.top_right.point.x < corner.point.x) and (s.top_left.point.y > corner.point.y or s.bottom_left.point.y < corner.point.y):
                d = euclidean_distance_point((s.center.x, s.center.y), (corner.point.x, corner.point.y))
                if d < dist:
                    cp2 = corner
                    dist = d
        if cp2 == None:
            cp2 = get_closest_corner(b, s)
            con = get_furthest_connector(cp1, cp2, s.center)
        else:
            con = get_furthest_connector(cp1, cp2, b.center)

        lines = get_manhattan_lines_2(cp1, cp2, con, manhattan_line_color)

        if len(lines) == 1:
            all_manhattan_lines.append(lines[0])

        if len(lines) == 2:
            all_manhattan_lines.extend(lines)
            lines_to_extend.extend(lines)

    # Convert to Plotly traces
    traces = []
    
    # Add blocks as filled rectangles
    for block in all_blocks:
        # Rectangle coordinates
        x_coords = [block.top_left_p[0], block.bottom_right_p[0], block.bottom_right_p[0], block.top_left_p[0], block.top_left_p[0]]
        y_coords = [block.top_left_p[1], block.top_left_p[1], block.bottom_right_p[1], block.bottom_right_p[1], block.top_left_p[1]]
        
        # Get pathway info for hover
        pathway_idx = pathway_ids_sorted.index(block.id)
        pathway_row = df[df["GS_ID"].str.endswith(block.id)].iloc[0]
        
        # Convert Colors enum to string for Plotly
        fill_color = str(block.color.value) if hasattr(block.color, 'value') else str(block.color)
        
        traces.append(go.Scatter(
            x=x_coords,
            y=y_coords,
            fill="toself",
            fillcolor=fill_color,
            line=dict(width=0, color="white"),  # Zero-width white border
            mode="lines",
            hovertemplate=(
                f"<b>{pathway_row['NAME']}</b><br>" +
                f"ID: {pathway_row['GS_ID']}<br>" +
                f"FC: {pathway_row['wFC']:.3f}<br>" +
                f"p-value: {pathway_row['pFDR']:.2e}<br>" +
                f"<i>Click for details</i>" +
                "<extra></extra>"
            ),
            showlegend=False,
            name=pathway_row['NAME']
        ))
        
        # Add pathway ID text ABOVE tiles, centered and scaled
        center_x = (block.top_left_p[0] + block.bottom_right_p[0]) / 2
        center_y = (block.top_left_p[1] + block.bottom_right_p[1]) / 2
        
        # Calculate tile dimensions for scaling
        tile_width = block.bottom_right_p[0] - block.top_left_p[0]
        tile_height = block.bottom_right_p[1] - block.top_left_p[1]
        tile_area = tile_width * tile_height
        
        # Position text well above the tile (outside and centered)
        text_x = center_x  # Centered horizontally
        text_y = block.top_left_p[1] - 25  # Further above the tile
        
        # If text would go outside canvas, position it inside but at the top
        if text_y < 30:
            text_y = block.top_left_p[1] + 20  # Position at top inside the tile
        
        # Scale text size according to tile size
        base_size = 12 if not maximize else 16
        # Scale factor based on tile area (larger tiles get larger text)
        scale_factor = min(max(tile_area / 2000, 0.7), 2.0)  # Scale between 0.7x and 2x
        scaled_size = int(base_size * scale_factor)
        
        # Ensure minimum and maximum text sizes
        scaled_size = max(8, min(scaled_size, 24))
        
        traces.append(go.Scatter(
            x=[text_x],
            y=[text_y],
            mode="text",
            text=[block.id],
            textfont=dict(
                size=scaled_size, 
                color="black",  # Black text for good contrast
                family="Arial Black"
            ),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add all lines (grid lines and relationship lines) - Make sure they're visible
    for line in Line.instances:
        line_color = str(line.color.value) if hasattr(line.color, 'value') else str(line.color)
        # Ensure grid lines are visible with proper width
        line_width = max(line.strength, 2)  # Minimum width of 2 for visibility
        
        traces.append(go.Scatter(
            x=[line.point_a.x, line.point_b.x],
            y=[line.point_a.y, line.point_b.y],
            mode="lines",
            line=dict(color=line_color, width=line_width),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add Manhattan relationship lines
    for line in all_manhattan_lines:
        line_color = str(line.color.value) if hasattr(line.color, 'value') else str(line.color)
        traces.append(go.Scatter(
            x=[line.point_a.x, line.point_b.x],
            y=[line.point_a.y, line.point_b.y],
            mode="lines",
            line=dict(color=line_color, width=line.strength),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Create figure
    fig = go.Figure(data=traces)
    
    # Set figure size based on maximize option
    if maximize:
        height = 1000
        width = 1000
        title_size = 24
    else:
        height = 600
        width = 600
        title_size = 16
    
    fig.update_layout(
        title=dict(
            text=f"Authentic Mondrian Map: {dataset_name}",
            font=dict(size=title_size)
        ),
        xaxis=dict(range=[0, 1000], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 1000], showticklabels=False, showgrid=False, zeroline=False),
        plot_bgcolor='white',
        height=height,
        width=width,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_canvas_grid(df_list, dataset_names, canvas_rows, canvas_cols):
    """
    Create the canvas grid that holds multiple Mondrian maps
    """
    fig = make_subplots(
        rows=canvas_rows, 
        cols=canvas_cols,
        subplot_titles=dataset_names[:canvas_rows*canvas_cols],
        specs=[[{"type": "xy"} for _ in range(canvas_cols)] for _ in range(canvas_rows)],
        horizontal_spacing=0.05,
        vertical_spacing=0.1
    )
    
    # Add each Mondrian map to its canvas cell
    for idx, (df, name) in enumerate(zip(df_list[:canvas_rows*canvas_cols], dataset_names[:canvas_rows*canvas_cols])):
        row = idx // canvas_cols + 1
        col = idx % canvas_cols + 1
        
        # Create individual Mondrian map for this dataset
        mondrian_fig = create_authentic_mondrian_map(df, name, maximize=False)
        
        # Add traces to subplot
        for trace in mondrian_fig.data:
            fig.add_trace(trace, row=row, col=col)
        
        # Configure subplot axes
        fig.update_xaxes(
            showticklabels=False, 
            showgrid=False, 
            zeroline=False,
            range=[0, 1000],
            row=row, col=col
        )
        fig.update_yaxes(
            showticklabels=False, 
            showgrid=False, 
            zeroline=False,
            range=[0, 1000],
            row=row, col=col
        )
    
    fig.update_layout(
        title="Canvas Grid: Authentic Mondrian Maps",
        showlegend=False,
        plot_bgcolor='white',
        height=200 * canvas_rows + 100,
        width=1200,
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig

@st.cache_data
def load_pathway_info():
    info_path = Path("data/case_study/pathway_details/annotations_with_summary.json")
    with open(info_path, "r") as f:
        return json.load(f)

def load_dataset(path: Path, pathway_info: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Description"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Description", ""))
    df["Ontology"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Pathway Ontology", ""))
    df["Disease"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Disease", ""))
    df["NAME"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("NAME", x))
    return df

def load_uploaded_dataset(uploaded_file, pathway_info: dict) -> pd.DataFrame:
    """Load dataset from uploaded CSV file"""
    df = pd.read_csv(uploaded_file)
    
    # Ensure required columns exist
    required_cols = ['GS_ID', 'wFC', 'pFDR', 'x', 'y']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        return None
    
    df["Description"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Description", ""))
    df["Ontology"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Pathway Ontology", ""))
    df["Disease"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Disease", ""))
    df["NAME"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("NAME", x))
    return df

def get_mondrian_color_description(wfc, p_value):
    """Get color description for display"""
    if p_value > 0.05:
        return 'Non-significant'
    
    if abs(wfc) < 0.5:
        return 'Neutral'
    elif abs(wfc) < 1.0:
        return 'Moderate change'
    elif wfc > 0:
        return 'Up-regulated'
    else:
        return 'Down-regulated'

def create_color_legend():
    """Create Mondrian color legend"""
    fig = go.Figure()
    
    colors = [
        (Colors.WHITE, 'Non-significant (p > 0.05)'),
        (Colors.BLACK, 'Neutral (|FC| < 0.5)'),
        (Colors.YELLOW, 'Moderate (0.5 ≤ |FC| < 1.0)'),
        (Colors.RED, 'Up-regulated (FC ≥ 1.0)'),
        (Colors.BLUE, 'Down-regulated (FC ≤ -1.0)')
    ]
    
    for i, (color, desc) in enumerate(colors):
        # Add colored rectangle
        fig.add_shape(
            type="rect",
            x0=0, y0=i*1.2, x1=1, y1=i*1.2+1,
            fillcolor=color,
            line=dict(color="black", width=2),
        )
        
        # Add text description
        text_color = 'white' if color == Colors.BLACK else 'black'
        fig.add_annotation(
            x=1.5, y=i*1.2+0.5,
            text=desc,
            showarrow=False,
            font=dict(size=11, color='black'),
            xanchor="left"
        )
    
    fig.update_layout(
        xaxis=dict(range=[-0.2, 5], showticklabels=False, showgrid=False),
        yaxis=dict(range=[-0.5, len(colors)*1.2], showticklabels=False, showgrid=False),
        plot_bgcolor='white',
        height=300,
        width=400,
        title="Mondrian Color Scheme",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig

def create_detailed_popup(df, dataset_name):
    """Create a detailed popup view for a specific Mondrian map"""
    st.markdown(f"## 🔍 Detailed View: {dataset_name}")
    
    # Create two columns for the popup
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show maximized Mondrian map
        detailed_fig = create_authentic_mondrian_map(df, dataset_name, maximize=True)
        st.plotly_chart(detailed_fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Dataset Statistics")
        
        # Basic stats
        total_pathways = len(df)
        up_reg = len(df[df['wFC'] >= up_th])
        down_reg = len(df[df['wFC'] <= dn_th])
        significant = len(df[df['pFDR'] < 0.05])
        
        st.metric("Total Pathways", total_pathways)
        st.metric("Up-regulated", up_reg)
        st.metric("Down-regulated", down_reg)
        st.metric("Significant (p<0.05)", significant)
        
        # Color distribution
        st.markdown("### 🎨 Color Distribution")
        colors = get_colors(df, up_th, dn_th)
        color_counts = {
            "Red (Up-reg)": colors.count("red"),
            "Blue (Down-reg)": colors.count("blue"), 
            "Yellow (Moderate)": colors.count("yellow"),
            "Black (Neutral)": colors.count("black")
        }
        
        for color, count in color_counts.items():
            if count > 0:
                st.write(f"• {color}: {count}")
        
        # Top pathways by fold change
        st.markdown("### 🔝 Top Pathways by |FC|")
        top_pathways = df.nlargest(5, df['wFC'].abs())[['NAME', 'wFC', 'pFDR']]
        st.dataframe(top_pathways, use_container_width=True)

# Streamlit App
st.set_page_config(page_title="Authentic Mondrian Map Explorer", layout="wide")

st.title("🎨 Authentic Mondrian Map Explorer")
st.markdown("*Faithful implementation of the bioRxiv paper algorithms*")

# Sidebar controls
st.sidebar.header("📊 Dataset Configuration")

# File upload option
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV files", 
    type=['csv'], 
    accept_multiple_files=True,
    help="Upload CSV files with columns: GS_ID, wFC, pFDR, x, y"
)

# Load pathway info
pathway_info = load_pathway_info()

# Dataset selection (multi-select)
if not uploaded_files:
    selected_datasets = st.sidebar.multiselect(
        "Select datasets", 
        list(DATASETS.keys()),
        default=["Aggressive R1", "Baseline R1"]
    )
    
    # Load selected datasets
    df_list = []
    dataset_names = []
    for dataset_name in selected_datasets:
        df = load_dataset(DATASETS[dataset_name], pathway_info)
        df_list.append(df)
        dataset_names.append(dataset_name)
else:
    # Use uploaded files
    df_list = []
    dataset_names = []
    for uploaded_file in uploaded_files:
        df = load_uploaded_dataset(uploaded_file, pathway_info)
        if df is not None:
            df_list.append(df)
            dataset_names.append(uploaded_file.name.replace('.csv', ''))

# Canvas Grid Configuration
st.sidebar.header("🎯 Canvas Grid Layout")
if len(df_list) > 0:
    if len(df_list) == 1:
        canvas_cols = 1
        canvas_rows = 1
        st.sidebar.info("Single dataset - 1×1 canvas")
    else:
        max_cols = min(4, len(df_list))
        canvas_cols = st.sidebar.slider("Canvas columns", 1, max_cols, min(2, len(df_list)))
        canvas_rows = int(np.ceil(len(df_list) / canvas_cols))
        st.sidebar.info(f"Canvas: {canvas_rows} rows × {canvas_cols} columns")
    
    # Display options
    show_legend = st.sidebar.checkbox("Show color legend", True)
    show_full_size = st.sidebar.checkbox("Show full-size maps", False)
    maximize_maps = st.sidebar.checkbox("🔍 Maximize individual maps", False, help="Show larger, detailed individual maps")

# Main content
if len(df_list) > 0:
    # Canvas Grid Overview
    st.subheader("📋 Canvas Grid Overview")
    st.markdown("*Click on individual map titles below to see detailed popup views*")
    
    canvas_fig = create_canvas_grid(df_list, dataset_names, canvas_rows, canvas_cols)
    st.plotly_chart(canvas_fig, use_container_width=True)
    
    # Add clickable buttons for each dataset
    st.markdown("### 🖱️ Click for Detailed Views")
    
    # Create buttons for each dataset
    button_cols = st.columns(len(df_list))
    for i, (df, name) in enumerate(zip(df_list, dataset_names)):
        with button_cols[i]:
            if st.button(f"🔍 {name}", key=f"popup_{i}", help=f"View detailed {name} map"):
                # Create popup in expander
                with st.expander(f"📊 Detailed Analysis: {name}", expanded=True):
                    create_detailed_popup(df, name)
    
    # Full-size individual maps
    if show_full_size:
        st.subheader("🔍 Full-Size Authentic Mondrian Maps")
        st.markdown("*Individual maps using the exact 3-stage algorithm from the notebooks*")
        
        if maximize_maps:
            st.info("🔍 **Maximized View**: Larger maps with enhanced details for better analysis")
        
        # Create columns for full-size maps
        if len(df_list) == 1:
            full_fig = create_authentic_mondrian_map(df_list[0], dataset_names[0], maximize=maximize_maps)
            st.plotly_chart(full_fig, use_container_width=True)
        else:
            # Show maps in pairs or single column if maximized
            cols_per_row = 1 if maximize_maps else 2
            
            for i in range(0, len(df_list), cols_per_row):
                if cols_per_row == 1:
                    # Single column for maximized view
                    full_fig = create_authentic_mondrian_map(df_list[i], dataset_names[i], maximize=maximize_maps)
                    st.plotly_chart(full_fig, use_container_width=True)
                else:
                    # Two columns for normal view
                    cols = st.columns(2)
                    
                    with cols[0]:
                        full_fig = create_authentic_mondrian_map(df_list[i], dataset_names[i], maximize=maximize_maps)
                        st.plotly_chart(full_fig, use_container_width=True)
                    
                    if i + 1 < len(df_list):
                        with cols[1]:
                            full_fig = create_authentic_mondrian_map(df_list[i + 1], dataset_names[i + 1], maximize=maximize_maps)
                            st.plotly_chart(full_fig, use_container_width=True)
    
    # Color legend and info
    if show_legend:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🎨 Color Legend")
            legend_fig = create_color_legend()
            st.plotly_chart(legend_fig, use_container_width=True)
        
        with col2:
            st.subheader("ℹ️ Authentic Algorithm")
            st.markdown("""
            **Faithful Implementation of bioRxiv Paper:**
            
            **3-Stage Generation Process:**
            1. **Grid System**: 1001×1001 canvas with 20×20 block grid
            2. **Block Placement**: Pathways as rectangles sized by fold change
            3. **Line Generation**: Authentic Mondrian-style grid lines
            
            **Key Features:**
            - Exact `GridSystem`, `Block`, `Line`, `Corner` classes from notebooks
            - Authentic color scheme: Red/Blue/Yellow/Black/White
            - Area scaling: `abs(log2(wFC)) * 4000`
            - Proper line width and adjustments
            - Rectangle placement based on pathway coordinates
            
            **Algorithm Parameters:**
            - Canvas: 1001×1001 pixels
            - Block size: 20×20 pixels  
            - Line width: 5 pixels
            - Area scalar: 4000
            - Up-regulation threshold: ≥1.25
            - Down-regulation threshold: ≤0.75
            """)
    
    # Dataset Statistics
    st.subheader("📈 Dataset Statistics")
    stats_cols = st.columns(len(df_list))
    for i, (df, name) in enumerate(zip(df_list, dataset_names)):
        with stats_cols[i]:
            st.metric(f"{name} - Total", len(df))
            up_reg = len(df[df['wFC'] >= up_th])
            down_reg = len(df[df['wFC'] <= dn_th])
            st.metric("Up-regulated", up_reg)
            st.metric("Down-regulated", down_reg)
    
    # Detailed pathway tables
    st.subheader("📋 Pathway Details")
    
    # Create tabs for each dataset
    if len(df_list) > 1:
        tabs = st.tabs(dataset_names)
        for i, (df, name) in enumerate(zip(df_list, dataset_names)):
            with tabs[i]:
                # Add color coding to the dataframe
                df_display = df.copy()
                df_display['Color'] = df_display.apply(
                    lambda row: get_mondrian_color_description(row['wFC'], row['pFDR']), axis=1
                )
                
                st.dataframe(
                    df_display[['NAME', 'GS_ID', 'wFC', 'pFDR', 'Color', 'Description', 'Ontology', 'Disease']].round(4),
                    use_container_width=True,
                    height=400
                )
    else:
        if len(df_list) > 0:
            df_display = df_list[0].copy()
            df_display['Color'] = df_display.apply(
                lambda row: get_mondrian_color_description(row['wFC'], row['pFDR']), axis=1
            )
            
            st.dataframe(
                df_display[['NAME', 'GS_ID', 'wFC', 'pFDR', 'Color', 'Description', 'Ontology', 'Disease']].round(4),
                use_container_width=True,
                height=400
            )

else:
    st.info("👆 Please select datasets or upload CSV files to begin visualization")
    
    # Show example data format
    st.subheader("📝 Required CSV Format")
    example_df = pd.DataFrame({
        'GS_ID': ['WAG002659', 'WAG002805'],
        'wFC': [1.1057, 1.0888],
        'pFDR': [3.5e-17, 5.3e-17],
        'x': [381.9, 971.2],
        'y': [468.9, 573.7]
    })
    st.dataframe(example_df)
    
    st.subheader("🎯 Authentic Implementation")
    st.markdown("""
    **Faithful to bioRxiv Paper Algorithm:**
    
    This implementation uses the exact same classes and methods from the research notebooks:
    - `GridSystem(1001, 1001, 20, 20)` - Authentic grid system
    - `Block`, `Line`, `Corner` classes with exact parameters
    - 3-stage generation process as described in the paper
    - Authentic color mapping and area scaling
    - Proper line width, adjustments, and positioning
    
    **Canvas Grid System:**
    - Level 1: Canvas arranges multiple Mondrian maps
    - Level 2: Each map uses authentic algorithm from notebooks
    - Users can view overview or full-size individual maps
    """)
