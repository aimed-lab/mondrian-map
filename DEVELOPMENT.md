# 🛠️ Development Guide

This guide is for developers who want to contribute to or extend the Mondrian Map project.

## 📁 Project Architecture

### Modular Structure
```
src/mondrian_map/           # Core Python package
├── core.py                # Algorithm classes (GridSystem, Block, Line)
├── data_processing.py     # Data loading and processing utilities  
├── visualization.py       # Plotly visualization functions
└── cli.py                 # Command-line interface

apps/                      # User-facing applications
└── streamlit_app.py       # Main Streamlit web application

config/                    # Configuration files
├── requirements.txt       # Dependencies
└── deployment configs...

deployment/               # Deployment documentation
docs/                     # User documentation
```

## 🚀 Development Setup

```bash
# Clone and setup
git clone https://github.com/your-username/mondrian-map.git
cd mondrian-map

# Install in development mode
pip install -e .
pip install -r config/requirements.txt

# Test installation
python -c "from mondrian_map.core import GridSystem; print('✅ Works!')"
streamlit run apps/streamlit_app.py
```

## 🧬 Core Architecture

### Key Classes
- **`GridSystem`**: Manages 1001×1001 canvas with 20×20 blocks
- **`Block`**: Represents pathway tiles with colors and positions
- **`Line`**: Grid lines and pathway connections
- **`Corner`**: Block corners for connection algorithms

### Algorithm Flow
1. **Data Preparation**: Load pathways, calculate areas, determine colors
2. **Grid Generation**: Place blocks on grid system
3. **Visualization**: Convert to Plotly traces with interactions

## 🎨 Adding Features

### New Visualization Type
```python
# In visualization.py
def create_custom_mondrian_map(df, **kwargs):
    grid_system = GridSystem(1001, 1001, 20, 20)
    # Your custom logic here
    return fig
```

### New Data Source
```python
# In data_processing.py  
def load_new_format(file_path):
    # Load and convert to standard format
    # Must have: GS_ID, wFC, pFDR, x, y
    return standardized_df
```

## 🧪 Testing & Quality

```bash
# Code formatting
black src/ apps/ --line-length 88

# Type checking  
mypy src/mondrian_map/

# Run tests
pytest tests/
```

## 📚 Documentation

- Add docstrings to all functions
- Update README for new features  
- Include examples in notebooks/
- Keep deployment docs current

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Follow code style
4. Add tests
5. Update docs
6. Submit PR

---

For detailed instructions, see the full documentation in the `docs/` folder. 