# NDB CSV Processor

A powerful CSV data processor designed for Network Database (NDB) files with transformation capabilities and multiple output formats.

## Author
**Hadi Fauzan Hanif**  
Email: hadifauzanhanif@gmail.com

## Features

### Core Processing
- **Data Transformation**: Advanced data transformation following VBA Module1.bas logic
- **Fixed_Ant_Size Mapping**: Intelligent antenna size mapping based on CELL_SYSTEM_INFO
- **Class_Cell Extraction**: Automatic cell classification from CELL_NAME patterns (L18_A01, 5G21_B02, etc.)
- **Multiple Output Formats**: Generate 3 different output files from single input

### Output Files
1. **`[input]_for_qgis_make_sector_NDB.txt`** - Transformed data for QGIS (24+ columns)
2. **`[input]_for_raw_TA_and_audit.csv`** - Main file for TA and audit (10 columns)
3. **`[input]_for_raw_1st_tier.csv`** - Simplified file for 1st tier analysis (5 columns)

### Performance
- **Fast Processing**: ~1-2 minutes for 500K+ rows
- **Memory Efficient**: Optimized with pandas for large datasets
- **Multi-threading**: Responsive GUI with background processing

### User Interface
- **Console Mode**: `main_processor.py` - Command line interface
- **GUI Mode**: `ndb_processor_gui.py` - Professional GUI using Dear PyGui
- **Filter Options**: Region and Site ID filtering capabilities
- **Real-time Logging**: Progress tracking and detailed logging

## Technical Specifications

### Transformation Logic
- **GSM900**: Antenna size 0.03
- **LTE1800**: Antenna size 0.095
- **LTE2100**: Antenna size 0.085
- **LTE900**: Antenna size 0.1
- **DCS1800**: Antenna size 0.02
- **5G18**: Antenna size 0.07
- **5G21**: Antenna size 0.065
- **5G_26G**: Antenna size 0.065
- **L18**: Antenna size 0.09
- **L21**: Antenna size 0.08
- **INDOOR Sites**: Antenna size divided by 4

### Column Mapping
The processor intelligently maps and filters columns according to predefined rules:
- Site ID, Longitude, Latitude, Direction, Antenna Beamwidth
- Antenna Size, Sector, EUtranCell, Cell ID, Class_Cell
- And many more standardized network parameters

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Dependencies
- pandas>=2.0.0
- polars>=0.20.0
- dearpygui>=1.9.0
- numpy
- pathlib

## Usage

### Console Mode
```bash
python main_processor.py
```

### GUI Mode
```bash
python ndb_processor_gui.py
```

### Processing Steps
1. **Step 1**: Select input CSV file
2. **Step 2**: Choose output directory
3. **Step 3**: (Optional) Set region and Site ID filters
4. **Step 4**: Click "Start Process" to begin transformation

## File Structure
```
NDB-CSV-Processor/
├── main_processor.py          # Console interface
├── ndb_processor_gui.py       # GUI interface  
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── LICENSE.txt                # License
└── HFH.ico                    # Application icon
```

## Input Format
- **File Type**: CSV format
- **Encoding**: UTF-8 recommended
- **Size**: Optimized for large files (500K+ rows)
- **Required Columns**: CELL_SYSTEM_INFO, CELL_NAME, site identifiers

## Output Format
All outputs maintain data integrity while providing different levels of detail for various use cases:
- **QGIS File**: Complete dataset with transformations
- **Audit File**: Essential columns for technical analysis  
- **1st Tier**: Simplified dataset for quick analysis

## Performance Notes
- Processing time scales linearly with input size
- Memory usage optimized for large datasets
- GUI remains responsive during processing
- Background threading prevents interface freezing

## Troubleshooting

### Common Issues
1. **File Access Error**: Ensure CSV file is not open in other applications
2. **Memory Error**: Close other applications for very large files
3. **Permission Error**: Check write permissions in output directory

### Support
For technical support and feature requests:
- Email: hadifauzanhanif@gmail.com
- Include error logs and sample data (anonymized)

## License
This software is provided under custom license terms. See LICENSE.txt for details.

## Version History
- **v1.0.0**: Initial release with core processing capabilities

---
*Developed with ❤️ by Hadi Fauzan Hanif* 