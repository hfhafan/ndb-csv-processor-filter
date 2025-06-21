#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Column Settings Manager
Save and load user column preferences
"""

import os
import json
from pathlib import Path

def get_settings_file():
    """Get path to column settings file"""
    try:
        # Get user documents folder
        if os.name == 'nt':  # Windows
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        else:  # Linux/Mac
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        
        # Create NDB CSV Processor folders
        app_folder = os.path.join(documents_path, 'NDB CSV Processor')
        settings_folder = os.path.join(app_folder, 'settings')
        
        # Create directories if they don't exist
        os.makedirs(settings_folder, exist_ok=True)
        
        return os.path.join(settings_folder, 'column_settings.json')
        
    except Exception:
        # Fallback to current directory
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'column_settings.json')

def save_column_settings(allowed_columns):
    """Save column settings to file"""
    try:
        settings_file = get_settings_file()
        settings_data = {
            'allowed_columns': allowed_columns,
            'version': '1.0',
            'saved_at': str(Path().absolute())
        }
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)
            
        return True
        
    except Exception as e:
        print(f"Failed to save column settings: {e}")
        return False

def load_column_settings():
    """Load column settings from file"""
    try:
        settings_file = get_settings_file()
        
        if not os.path.exists(settings_file):
            # Return default settings if file doesn't exist
            return get_default_columns()
            
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
            
        # Validate data structure
        if 'allowed_columns' in settings_data and isinstance(settings_data['allowed_columns'], list):
            return settings_data['allowed_columns']
        else:
            return get_default_columns()
            
    except Exception as e:
        print(f"Failed to load column settings: {e}")
        return get_default_columns()

def get_default_columns():
    """Get default column list"""
    return [
        "SITE_ID", "SiteID", "site_id", "Longitude", "X_LONGITUDE", "LONG", "LON",
        "Latitude", "Y_LATITUDE", "LAT", "ANTENNA_TYPE", "AntennaType", "Antenna_Type",
        "Fixed_Ant_Size", "FixedSize", "AntSize", "SECTOR_TYPE", "SectorType", "sector_type",
        "CELL_ID", "CellID", "cell_id", "ANTENNA_AZIMUTH_DEG", "Azimuth", "AZIMUTH",
        "SITE_NAME", "SITE NAME", "SITENAME", "CELL_NAME", "CELL", "CELL NAME",
        "CITY_OR_DATI_II", "CITY", "CLUTTER", "AREA", "BRANCH", "PROVINCE", "REGION",
        "HEIGHT_ANTENNA_M", "HEIGHT_ANTENNA", "ANTENNA_HEIGHT", "HEIGHT",
        "HORIZONTAL_BEAMWIDTH_DEG", "Beamwidth", "BEAMWIDTH", "Class_Cell", "ClassCell", 
        "Cell_Class", "CELL_SYSTEM_INFO", 
        "Nano_Cluster", "Cluster", "Nano Cluster", "Vendor", "BTS_VENDOR", 
        "BCCH_OR_TRX1_Freq", "LAC", "PCI", "TAC_4G"
    ] 