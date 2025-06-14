# Release Notes - Mondrian Map Explorer

## Version 1.1.0 (December 14, 2025)

### 🎉 Major Release: Authentic Mondrian Map Web Application

This release introduces a complete interactive web application that faithfully implements the authentic Mondrian Map algorithm from our bioRxiv paper "Mondrian Abstraction and Language Model Embeddings for Differential Pathway Analysis".

---

## 🆕 New Features

### 🎨 Authentic Algorithm Implementation
- **Complete Class System**: Implemented exact `GridSystem`, `Block`, `Line`, `Corner` classes with parameters matching the research notebooks
- **3-Stage Generation Process**: 
  1. Block placement based on pathway coordinates and fold change
  2. Manhattan relationship lines connecting related pathways
  3. Line extensions for complete Mondrian aesthetic
- **Authentic Color Scheme**: 
  - Red: Up-regulated pathways (FC ≥ 1.25)
  - Blue: Down-regulated pathways (FC ≤ 0.75)
  - Yellow: Moderate change pathways
  - Black: Neutral pathways
  - White: Non-significant pathways (p > 0.05)
- **Area Scaling**: Exact `abs(log2(wFC)) * 4000` formula from the paper
- **Light Gray Grid Lines**: Authentic Mondrian appearance with outer boundary and internal grid lines

### 🖼️ Interactive Web Application
- **Streamlit-based Interface**: Professional, responsive web application
- **Canvas Grid System**: Compare multiple datasets simultaneously in customizable grid layouts (1×1 to 4×4)
- **Detailed Popup Views**: Click any dataset button for comprehensive analysis with:
  - Maximized Mondrian map (1000×1000 pixels)
  - Dataset statistics (total pathways, up/down-regulated counts)
  - Color distribution analysis
  - Top pathways by fold change
- **Adaptive Text Scaling**: Pathway labels scale with tile size (8-24px range)
- **Smart Label Positioning**: Labels positioned above tiles with fallback to inside positioning

### 📊 Data Integration & Analysis
- **Multi-Dataset Support**: All 6 pre-computed datasets from the glioblastoma case study
  - Aggressive R1/R2
  - Baseline R1/R2  
  - Nonaggressive R1/R2
- **Pathway Network Integration**: Manhattan connection lines based on pathway relationships
- **File Upload Capability**: Support for custom CSV datasets with validation
- **Complete Annotation System**: Integration with pathway descriptions, ontology, and disease information
- **Comprehensive Statistics**: Real-time analysis of pathway distributions and significance

### 🔧 User Interface & Experience
- **Multi-Select Configuration**: Choose any combination of datasets for comparison
- **Viewing Modes**:
  - Canvas Grid Overview: Side-by-side dataset comparison
  - Full-Size Individual Maps: Detailed single-dataset views
  - Maximized Mode: Enhanced detail for analysis
- **Interactive Controls**:
  - Toggle color legend display
  - Toggle full-size map views
  - Maximize individual maps option
  - Customizable canvas grid dimensions
- **Professional Tooltips**: Rich hover information with pathway details
- **Color Legend**: Visual guide to the Mondrian color scheme

---

## 🔧 Technical Improvements

### Algorithm Fidelity
- **Exact Parameter Matching**: All constants match the research implementation
  - Canvas: 1001×1001 pixels
  - Block size: 20×20 pixels
  - Line width: 5px (borders), 1px (grid lines), minimum 2px for visibility
  - Area scalar: 4000
- **Proper Line Rendering**: Ensured grid lines are visible with appropriate width
- **Border Handling**: Zero-width white borders for clean tile appearance
- **Color Enum Integration**: Proper conversion between Python enums and Plotly requirements

### Performance & Reliability
- **Efficient Data Loading**: Cached pathway information loading
- **Error Handling**: Robust file upload validation and error messages
- **Memory Management**: Proper canvas clearing between generations
- **Responsive Design**: Optimized for different screen sizes and viewing modes

### Code Architecture
- **Modular Design**: Separated concerns for algorithm, visualization, and UI
- **Helper Functions**: Complete set of utility functions from research notebooks
- **Type Safety**: Proper type hints and enum usage
- **Documentation**: Comprehensive inline documentation and help text

---

## 📈 Data & Integration

### Pathway Data
- **Complete Dataset Coverage**: All pathways from the glioblastoma case study
- **Rich Annotations**: NAME, Description, Ontology, Disease information
- **Network Relationships**: Pathway-pathway connection data for Manhattan lines
- **Coordinate System**: Exact x,y positioning from the research

### File Format Support
- **CSV Upload**: Support for custom datasets with required columns:
  - `GS_ID`: Gene set/pathway identifier
  - `wFC`: Weighted fold change
  - `pFDR`: Adjusted p-value (FDR)
  - `x`, `y`: Coordinates for positioning
- **Validation**: Automatic checking for required columns and data types
- **Error Reporting**: Clear messages for data format issues

---

## 🎯 User Experience Enhancements

### Navigation & Interaction
- **Intuitive Interface**: Clear section organization and navigation
- **Contextual Help**: Tooltips and help text throughout the application
- **Responsive Feedback**: Real-time updates and loading indicators
- **Professional Styling**: Modern UI design with consistent theming

### Analysis Features
- **Statistical Overview**: Comprehensive dataset statistics
- **Comparative Analysis**: Side-by-side dataset comparison
- **Detailed Exploration**: Deep-dive analysis with maximized views
- **Export-Ready Visualizations**: High-quality plots suitable for presentations

---

## 🔄 Migration from Version 1.0

### What's Changed
- **Complete Application Rewrite**: From simple scatter plots to authentic Mondrian maps
- **Enhanced Data Integration**: From basic CSV loading to comprehensive pathway analysis
- **Professional UI**: From basic Streamlit interface to feature-rich application

### Backward Compatibility
- **Data Format**: Maintains compatibility with existing CSV data files
- **Core Functionality**: All original research capabilities preserved and enhanced
- **Notebook Integration**: Research notebooks remain functional alongside the web app

---

## 🐛 Bug Fixes & Improvements

### Visual Fixes
- **Grid Line Visibility**: Ensured all grid lines are properly visible
- **Text Positioning**: Fixed label positioning issues with proper centering and fallback
- **Color Consistency**: Resolved color enum conversion issues
- **Border Rendering**: Achieved clean borderless tile appearance

### Performance Improvements
- **Faster Rendering**: Optimized Plotly trace generation
- **Memory Usage**: Improved canvas clearing and object management
- **Loading Times**: Cached data loading for better responsiveness

---

## 📋 Requirements

### System Requirements
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB+ RAM recommended for large datasets

### Dependencies
- streamlit
- plotly
- pandas
- numpy
- pathlib

### Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔮 Future Roadmap

### Planned Features
- **Export Functionality**: Save high-resolution images and data
- **Advanced Filtering**: Filter pathways by various criteria
- **Batch Processing**: Process multiple datasets simultaneously
- **API Integration**: REST API for programmatic access
- **Enhanced Analytics**: Statistical testing and comparison tools

### Community Contributions
We welcome contributions! Please see our contribution guidelines and open issues on GitHub.

---

## 📞 Support & Contact

For questions, bug reports, or feature requests:
- **Email**: [jakechen@uab.edu](mailto:jakechen@uab.edu) or [fuad021@uab.edu](mailto:fuad021@uab.edu)
- **GitHub Issues**: [https://github.com/aimed-lab/mondrian-map/issues](https://github.com/aimed-lab/mondrian-map/issues)
- **Documentation**: See README.md for detailed usage instructions

---

## 📄 Citation

If you use this software in your research, please cite our paper:

```bibtex
@article {AlAbir_MondrianMap,
	author = {Al Abir, Fuad and Chen, Jake Y.},
	title = {Mondrian Abstraction and Language Model Embeddings for Differential Pathway Analysis},
	elocation-id = {2024.04.11.589093},
	year = {2024},
	doi = {10.1101/2024.04.11.589093},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2024/08/19/2024.04.11.589093},
	eprint = {https://www.biorxiv.org/content/early/2024/08/19/2024.04.11.589093.full.pdf},
	journal = {bioRxiv}
}
```

---

*Thank you for using Mondrian Map Explorer! We hope this tool enhances your pathway analysis research.* 