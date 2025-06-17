"""
Command Line Interface for Mondrian Map

This module provides a simple CLI for running Mondrian Map visualizations.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

from .data_processing import load_pathway_info, load_dataset
from .visualization import create_authentic_mondrian_map

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Mondrian Maps for pathway visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mondrian-map --input data.csv --output map.html
  mondrian-map --input data.csv --output map.png --format png
  mondrian-map --help
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input CSV file with pathway data"
    )
    
    parser.add_argument(
        "--output", "-o", 
        required=True,
        help="Output file path"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["html", "png", "pdf", "svg"],
        default="html",
        help="Output format (default: html)"
    )
    
    parser.add_argument(
        "--title", "-t",
        default="Mondrian Map",
        help="Title for the visualization"
    )
    
    parser.add_argument(
        "--pathway-info",
        help="Path to pathway info JSON file"
    )
    
    parser.add_argument(
        "--maximize",
        action="store_true",
        help="Create maximized (larger) visualization"
    )
    
    parser.add_argument(
        "--show-ids",
        action="store_true", 
        help="Show pathway IDs on tiles"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Load pathway info
    pathway_info = {}
    if args.pathway_info:
        pathway_info_path = Path(args.pathway_info)
        if pathway_info_path.exists():
            pathway_info = load_pathway_info(pathway_info_path)
        else:
            print(f"Warning: Pathway info file '{args.pathway_info}' not found")
    
    try:
        # Load data
        print(f"Loading data from {args.input}...")
        df = pd.read_csv(input_path)
        
        # Validate required columns
        required_cols = ['GS_ID', 'wFC', 'pFDR', 'x', 'y']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}", file=sys.stderr)
            sys.exit(1)
        
        # Add pathway info if available
        if pathway_info:
            df["Description"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("Description", ""))
            df["NAME"] = df["GS_ID"].map(lambda x: pathway_info.get(x, {}).get("NAME", x))
        else:
            df["Description"] = ""
            df["NAME"] = df["GS_ID"]
        
        # Create visualization
        print(f"Creating Mondrian Map for {len(df)} pathways...")
        fig = create_authentic_mondrian_map(
            df, 
            args.title,
            maximize=args.maximize,
            show_pathway_ids=args.show_ids
        )
        
        # Save output
        output_path = Path(args.output)
        print(f"Saving to {args.output}...")
        
        if args.format == "html":
            fig.write_html(output_path)
        elif args.format == "png":
            fig.write_image(output_path, format="png")
        elif args.format == "pdf":
            fig.write_image(output_path, format="pdf")
        elif args.format == "svg":
            fig.write_image(output_path, format="svg")
        
        print(f"✅ Mondrian Map saved successfully to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 