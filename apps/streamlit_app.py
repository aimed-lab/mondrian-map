"""
Authentic Mondrian Map Explorer - Streamlit Application

This is the main Streamlit application for visualizing biological pathway data
using authentic Mondrian Map algorithms from the bioRxiv paper.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Add the src directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from mondrian_map.core import Colors
from mondrian_map.data_processing import (
    load_pathway_info, load_dataset, load_uploaded_dataset, 
    get_mondrian_color_description, get_colors
)
from mondrian_map.visualization import (
    create_authentic_mondrian_map, create_canvas_grid, create_color_legend
)

# Configuration
DATA_DIR = Path("data/case_study/pathways_prepared_for_visualization")
DATASETS = {
    "Aggressive R1": DATA_DIR / "wikipathway_aggressive_R1_TP.csv",
    "Aggressive R2": DATA_DIR / "wikipathway_aggressive_R2_TP.csv",
    "Baseline R1": DATA_DIR / "wikipathway_baseline_R1_TP.csv",
    "Baseline R2": DATA_DIR / "wikipathway_baseline_R2_TP.csv",
    "Nonaggressive R1": DATA_DIR / "wikipathway_nonaggressive_R1_TP.csv",
    "Nonaggressive R2": DATA_DIR / "wikipathway_nonaggressive_R2_TP.csv",
}

@st.cache_data
def load_pathway_info_cached():
    """Load pathway info with caching"""
    info_path = Path("data/case_study/pathway_details/annotations_with_summary.json")
    return load_pathway_info(info_path)

def create_detailed_popup(df: pd.DataFrame, dataset_name: str):
    """Create a detailed popup view for a specific Mondrian map"""
    st.markdown(f"## 🔍 Detailed View: {dataset_name}")
    
    # Create two columns for the popup
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show maximized Mondrian map
        detailed_fig = create_authentic_mondrian_map(df, dataset_name, maximize=True, show_pathway_ids=True)
        st.plotly_chart(detailed_fig, use_container_width=True, key=f"detailed_{dataset_name}")
        
        st.info("💡 **Click pathway tiles** in the map above to see individual pathway details")
    
    with col2:
        st.markdown("### 📊 Dataset Statistics")
        
        # Basic stats
        total_pathways = len(df)
        up_reg = len(df[df['wFC'] >= 1.25])
        down_reg = len(df[df['wFC'] <= 0.75])
        significant = len(df[df['pFDR'] < 0.05])
        
        st.metric("Total Pathways", total_pathways)
        st.metric("Up-regulated", up_reg)
        st.metric("Down-regulated", down_reg)
        st.metric("Significant (p<0.05)", significant)
        
        # Color distribution
        st.markdown("### 🎨 Color Distribution")
        colors = get_colors(df, 1.25, 0.75)
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
        df_with_abs_fc = df.copy()
        df_with_abs_fc['abs_wFC'] = df_with_abs_fc['wFC'].abs()
        top_pathways = df_with_abs_fc.nlargest(5, 'abs_wFC')[['NAME', 'wFC', 'pFDR']]
        st.dataframe(top_pathways, use_container_width=True)

def main():
    """Main Streamlit application"""
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
    pathway_info = load_pathway_info_cached()

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
        show_pathway_ids = st.sidebar.checkbox("Show pathway IDs", False, help="Toggle pathway ID labels on tiles")
        show_full_size = st.sidebar.checkbox("Show full-size maps", False)
        maximize_maps = st.sidebar.checkbox("🔍 Maximize individual maps", False, help="Show larger, detailed individual maps")

    # Main content
    if len(df_list) > 0:
        # Canvas Grid Overview
        st.subheader("📋 Canvas Grid Overview")
        st.markdown("*Click on individual map titles below to see detailed popup views*")
        
        canvas_fig = create_canvas_grid(df_list, dataset_names, canvas_rows, canvas_cols, show_pathway_ids)
        
        # Display the canvas with click event handling
        canvas_container = st.container()
        with canvas_container:
            clicked_data = st.plotly_chart(canvas_fig, use_container_width=True, key="canvas_chart", on_select="rerun")
        
        # Add clickable functionality info
        st.markdown("### 🖱️ Interactive Maps")
        st.info("💡 **Click on any pathway tile** in the maps above to view it in full-screen detail mode")
        
        # Session state for managing detailed views
        if 'show_detailed_view' not in st.session_state:
            st.session_state.show_detailed_view = None
        
        # Check if any detailed view should be shown
        for i, (df, name) in enumerate(zip(df_list, dataset_names)):
            if st.session_state.show_detailed_view == name:
                st.markdown("---")
                create_detailed_popup(df, name)
                if st.button("❌ Close Detailed View", key=f"close_{i}"):
                    st.session_state.show_detailed_view = None
                    st.rerun()
        
        # Full-size individual maps
        if show_full_size:
            st.subheader("🔍 Full-Size Authentic Mondrian Maps")
            st.markdown("*Individual maps using the exact 3-stage algorithm from the notebooks*")
            
            if maximize_maps:
                st.info("🔍 **Maximized View**: Larger maps with enhanced details for better analysis")
            
            # Create columns for full-size maps
            if len(df_list) == 1:
                full_fig = create_authentic_mondrian_map(df_list[0], dataset_names[0], maximize=maximize_maps, show_pathway_ids=show_pathway_ids)
                st.plotly_chart(full_fig, use_container_width=True, key=f"full_map_0")
                st.info("💡 **Click on pathway tiles above** to view the dataset in full-screen detail mode")
            else:
                # Show maps in pairs or single column if maximized
                cols_per_row = 1 if maximize_maps else 2
                
                for i in range(0, len(df_list), cols_per_row):
                    if cols_per_row == 1:
                        # Single column for maximized view
                        full_fig = create_authentic_mondrian_map(df_list[i], dataset_names[i], maximize=maximize_maps, show_pathway_ids=show_pathway_ids)
                        st.plotly_chart(full_fig, use_container_width=True, key=f"full_map_{i}")
                        st.info("💡 **Click pathway tiles** to view in full-screen detail")
                    else:
                        # Two columns for normal view
                        cols = st.columns(2)
                        
                        with cols[0]:
                            full_fig = create_authentic_mondrian_map(df_list[i], dataset_names[i], maximize=maximize_maps, show_pathway_ids=show_pathway_ids)
                            st.plotly_chart(full_fig, use_container_width=True, key=f"full_map_{i}")
                            st.info("💡 **Click tiles** for details")
                        
                        if i + 1 < len(df_list):
                            with cols[1]:
                                full_fig = create_authentic_mondrian_map(df_list[i + 1], dataset_names[i + 1], maximize=maximize_maps, show_pathway_ids=show_pathway_ids)
                                st.plotly_chart(full_fig, use_container_width=True, key=f"full_map_{i+1}")
                                st.info("💡 **Click tiles** for details")
        
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
                up_reg = len(df[df['wFC'] >= 1.25])
                down_reg = len(df[df['wFC'] <= 0.75])
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

if __name__ == "__main__":
    main() 