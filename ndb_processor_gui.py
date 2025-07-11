#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDB CSV Processor v2.0.0
Advanced Network Database CSV Processing Tool

Professional GUI using Dear PyGui
Untuk memproses file CSV NDB dengan custom column settings dan persistent preferences

Author: Hadi Fauzan Hanif
GitHub: https://github.com/hadifauzan/ndb-csv-processor
© 2024 Hadi Fauzan Hanif
"""

import dearpygui.dearpygui as dpg
import threading
import queue
import time
import os
import sys
import ctypes
from pathlib import Path
import pandas as pd

# Import processing functions
from main_processor import NDBDataProcessor, FinalOutputGenerator, generate_output_names

# Login handling imports
from device_id import get_device_id
from registry import read_login_info, save_login_info
from auth import check_credentials
from login import login_menu

# Column settings imports
from column_settings import save_column_settings, load_column_settings, get_default_columns

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class NDBProcessorGUI:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Setup default paths in user documents
        self.setup_default_paths()
        
        self.input_file = ""
        self.output_dir = self.default_output_dir
        self.is_processing = False
        self.progress_queue = queue.Queue()
        self.log_queue = queue.Queue()
        
        # Filter options
        self.region_options = [
            "ALL REGIONS",
            "CENTRAL SUMATERA",
            "SOUTH SUMATERA", 
            "WEST JAVA",
            "OUTER JAKARTA",
            "INNER JAKARTA",
            "CENTRAL JAVA",
            "EAST JAVA",
            "BALI NUSRA",
            "KALIMANTAN",
            "SULAWESI",
            "MAPA",
            "NORTH SUMATERA"
        ]
        
        self.selected_regions = []
        self.site_id_filter = ""
        
        # Processing results
        self.results = {
            'step2': False, 
            'step4': False,
            'files': []
        }
        
        # Load allowed columns from saved settings
        self.allowed_columns_raw = load_column_settings()
        self.log_message("INIT", f"Loaded {len(self.allowed_columns_raw)} saved column settings")
        
    def setup_default_paths(self):
        """Setup default paths in user documents"""
        try:
            # Get user documents folder
            if os.name == 'nt':  # Windows
                documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            else:  # Linux/Mac
                documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            
            # Create NDB CSV Processor folders
            self.app_folder = os.path.join(documents_path, 'NDB CSV Processor')
            self.default_input_dir = os.path.join(self.app_folder, 'input')
            self.default_output_dir = os.path.join(self.app_folder, 'output')
            
            # Create directories if they don't exist
            os.makedirs(self.default_input_dir, exist_ok=True)
            os.makedirs(self.default_output_dir, exist_ok=True)
            
        except Exception as e:
            # Fallback to current directory if documents access fails
            self.app_folder = self.current_dir
            self.default_input_dir = self.current_dir
            self.default_output_dir = self.current_dir
        
    def setup_theme(self):
        """Setup elegant theme with Color Hunt palette"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Color Hunt Palette: EAEBD0-DA6C6C-CD5656-AF3E3E
                # Base colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (42, 42, 50), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (48, 48, 56), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (45, 45, 53), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (175, 62, 62), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (55, 55, 63), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (65, 65, 73), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (75, 75, 83), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (35, 35, 43), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (42, 42, 50), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (48, 48, 56), category=dpg.mvThemeCat_Core)
                
                # Accent colors using Color Hunt palette
                dpg.add_theme_color(dpg.mvThemeCol_Button, (205, 86, 86), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (218, 108, 108), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (175, 62, 62), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Header, (205, 86, 86), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (218, 108, 108), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (175, 62, 62), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (175, 62, 62), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (205, 86, 86), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (218, 108, 108), category=dpg.mvThemeCat_Core)
                
                # Text colors
                dpg.add_theme_color(dpg.mvThemeCol_Text, (234, 235, 208), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (160, 160, 160), category=dpg.mvThemeCat_Core)
                
                # Progress bar and other elements
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (218, 108, 108), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (205, 86, 86), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (48, 48, 56), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (175, 62, 62), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (205, 86, 86), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (218, 108, 108), category=dpg.mvThemeCat_Core)
                
                # Styling
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 12, 8, category=dpg.mvThemeCat_Core)
                
        dpg.bind_theme(global_theme)
        
    def log_message(self, step, message):
        """Add message to log queue"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{step}] {message}"
        self.log_queue.put(log_msg)
        
    def update_progress(self, value, text=""):
        """Update progress bar"""
        self.progress_queue.put((value, text))
        
    def browse_input_file(self):
        """Open file browser for CSV input"""
        def file_selected(sender, app_data):
            file_path = app_data['file_path_name']
            if file_path.lower().endswith('.csv'):
                self.input_file = file_path
                dpg.set_value("input_file_text", file_path)
                dpg.configure_item("process_button", enabled=True)
                self.log_message("FILE", f"Selected: {Path(file_path).name}")
            else:
                dpg.set_value("error_popup_text", "Please select a valid CSV file!")
                dpg.show_item("error_popup")
                
        with dpg.file_dialog(
            directory_selector=False, 
            show=True, 
            callback=file_selected, 
            file_count=1,
            default_path=self.default_input_dir,
            width=700, 
            height=400,
            modal=True
        ):
            dpg.add_file_extension(".csv", color=(205, 86, 86, 255))
            dpg.add_file_extension(".*", color=(150, 150, 150, 255))
            
    def browse_output_dir(self):
        """Browse output directory"""
        def dir_selected(sender, app_data):
            self.output_dir = app_data['file_path_name']
            dpg.set_value("output_dir_text", self.output_dir)
            self.log_message("DIR", f"Output dir: {Path(self.output_dir).name}")
            
        with dpg.file_dialog(
            directory_selector=True, 
            show=True, 
            callback=dir_selected,
            default_path=self.default_output_dir,
            width=700, 
            height=400,
            modal=True
        ):
            pass
        
    def apply_filters(self):
        """Apply region and site ID filters to processed data"""
        try:
            processed_file = os.path.join(self.output_dir, self.output_names['processed_txt'])
            if not os.path.exists(processed_file):
                self.log_message("ERROR", f"{self.output_names['processed_txt']} tidak ditemukan. Jalankan proses transformasi dulu.")
                return False
                
            self.log_message("FILTER", "Menerapkan filter region dan site ID...")
            
            # Load processed data
            df = pd.read_csv(processed_file, sep='\t', low_memory=False)
            original_rows = len(df)
            
            # Apply region filter
            if self.selected_regions and "ALL REGIONS" not in self.selected_regions:
                df = df[df['REGION'].isin(self.selected_regions)]
                self.log_message("FILTER", f"Filter region: {', '.join(self.selected_regions)}")
                
            # Apply site ID filter
            if self.site_id_filter.strip():
                site_ids = [s.strip() for s in self.site_id_filter.split(',') if s.strip()]
                if site_ids:
                    df = df[df['SITE_ID'].isin(site_ids)]
                    self.log_message("FILTER", f"Filter site ID: {', '.join(site_ids)}")
                    
            filtered_rows = len(df)
            self.log_message("FILTER", f"Rows: {original_rows:,} -> {filtered_rows:,}")
            
            # Save filtered data with new naming
            filtered_file = os.path.join(self.output_dir, f"FILTERED_{self.output_names['processed_txt']}")
            df.to_csv(filtered_file, sep='\t', index=False)
            
            self.log_message("FILTER", f"Data terfilter disimpan: {filtered_file}")
            return True
            
        except Exception as e:
            self.log_message("ERROR", f"Filter gagal: {str(e)}")
            return False
            
    def cleanup_intermediate_files(self):
        """Clean up intermediate files after processing"""
        try:
            # Only cleanup filtered intermediate file if filters were applied
            # Keep the main processed .txt file as final output
            if hasattr(self, 'selected_regions') and (self.selected_regions or self.site_id_filter.strip()):
                # If filters were applied, remove the non-filtered intermediate file
                unfiltered_file = os.path.join(self.output_dir, self.output_names['processed_txt'])
                if os.path.exists(unfiltered_file):
                    os.remove(unfiltered_file)
                    self.log_message("CLEANUP", f"Removed unfiltered intermediate: {Path(unfiltered_file).name}")
                    
                # Rename filtered file to final name
                filtered_file = os.path.join(self.output_dir, f"FILTERED_{self.output_names['processed_txt']}")
                final_file = os.path.join(self.output_dir, self.output_names['processed_txt'])
                if os.path.exists(filtered_file):
                    os.rename(filtered_file, final_file)
                    self.log_message("CLEANUP", f"Renamed filtered file to: {Path(final_file).name}")
            else:
                # No filters applied, keep the main file as is
                self.log_message("CLEANUP", "No filters applied, keeping main processed file")
                    
        except Exception as e:
            self.log_message("WARNING", f"Cleanup failed: {str(e)}")
            
    def process_step2(self):
        """Step 2: Process and transform CSV data"""
        try:
            self.update_progress(20, "Processing and transforming CSV data...")
            self.log_message("STEP2", "Starting CSV data transformation...")
            
            # Generate output names based on input file
            self.output_names = generate_output_names(self.input_file)
            
            # Create processor instance with custom allowed columns
            processor = NDBDataProcessor(self.input_file)
            processor.allowed_columns_raw = self.allowed_columns_raw  # Use GUI settings
            
            # Load and process data
            if not processor.load_data():
                raise Exception("Failed to load CSV data")
                
            self.update_progress(40, "Transforming data...")
            self.log_message("STEP2", f"Using {len(self.allowed_columns_raw)} allowed columns untuk TXT output")
            
            # Transform data
            transformed_df = processor.transform_data(processor.df)
            final_df = processor.filter_allowed_columns(transformed_df)
            
            # Save processed data with new naming
            output_file = os.path.join(self.output_dir, self.output_names['processed_txt'])
            final_df.to_csv(output_file, sep='\t', index=False)
            
            self.update_progress(60, "Data transformation completed!")
            self.results['step2'] = True
            self.results['files'].append((self.output_names['processed_txt'], output_file))
            return True
            
        except Exception as e:
            self.log_message("ERROR", f"Step 2 failed: {str(e)}")
            return False
            
    def process_step4(self):
        """Step 4: Create final outputs"""
        try:
            self.update_progress(70, "Creating final outputs...")
            self.log_message("STEP4", "Creating RAWNDB outputs...")
            
            # Change to output directory for processing
            old_cwd = os.getcwd()
            os.chdir(self.output_dir)
            
            try:
                # Check if we have filtered data, otherwise use processed data
                filtered_file = f"FILTERED_{self.output_names['processed_txt']}"
                input_file = filtered_file if os.path.exists(filtered_file) else self.output_names['processed_txt']
                
                generator = FinalOutputGenerator(input_file)
                success = generator.generate_final_outputs(self.output_names)
                
                if success:
                    self.update_progress(90, "Final outputs created!")
                    self.results['step4'] = True
                    
                    # Add output files to results with new names
                    for key, filename in self.output_names.items():
                        if key != 'processed_txt' and os.path.exists(filename):
                            self.results['files'].append((filename, os.path.join(self.output_dir, filename)))
                            
                    return True
                else:
                    raise Exception("Failed to generate final outputs")
                    
            finally:
                os.chdir(old_cwd)
                
        except Exception as e:
            self.log_message("ERROR", f"Step 4 failed: {str(e)}")
            return False
            
    def process_all_parallel(self):
        """Process all steps in parallel thread"""
        def worker():
            try:
                self.is_processing = True
                self.update_progress(5, "Starting processing...")
                
                # Step 2: Transform CSV data
                if not self.process_step2():
                    return
                    
                # Apply filters if any
                if self.selected_regions or self.site_id_filter.strip():
                    self.update_progress(65, "Applying filters...")
                    if not self.apply_filters():
                        return
                        
                # Step 4: Create final outputs
                if not self.process_step4():
                    return
                    
                # Cleanup intermediate files
                self.update_progress(95, "Cleaning up intermediate files...")
                self.cleanup_intermediate_files()
                    
                self.update_progress(100, "Processing completed successfully!")
                self.log_message("SUCCESS", "All processing completed!")
                
                # Auto open output folder
                self.open_output_folder()
                
            except Exception as e:
                self.log_message("ERROR", f"Processing failed: {str(e)}")
            finally:
                self.is_processing = False
                
        # Start worker thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    def stop_processing(self):
        """Stop current processing"""
        self.is_processing = False
        self.log_message("STOP", "Processing stopped by user")
        
    def show_results(self):
        """Show results in popup"""
        if not self.results['files']:
            dpg.set_value("error_popup_text", "Tidak ada file hasil yang ditemukan!")
            dpg.show_item("error_popup")
            return
            
        # Create results window
        with dpg.window(label="Hasil Processing", modal=True, show=True, 
                       width=600, height=400, pos=(100, 100)):
            
            dpg.add_text("File yang berhasil dibuat:", color=(218, 108, 108))
            dpg.add_spacer(height=5)
            
            for filename, filepath in self.results['files']:
                with dpg.group(horizontal=True):
                    dpg.add_text(f"- {filename}")
                    if os.path.exists(filepath):
                        size_mb = os.path.getsize(filepath) / (1024*1024)
                        dpg.add_text(f"({size_mb:.1f} MB)", color=(160, 160, 160))
                        
            dpg.add_spacer(height=10)
            dpg.add_text(f"Output directory: {self.output_dir}", color=(160, 160, 160))
            
            dpg.add_spacer(height=20)
            if dpg.add_button(label="Tutup", callback=lambda: dpg.delete_item(dpg.last_item())):
                pass
                
    def show_column_settings(self):
        """Show column settings window"""
        # Close existing window if open
        if dpg.does_item_exist("column_settings_window"):
            dpg.delete_item("column_settings_window")
            
        # Small delay to ensure cleanup
        import time
        time.sleep(0.01)
        
        with dpg.window(label="Setting Kolom Output TXT", modal=True, show=True, 
                       width=750, height=700, pos=(50, 50), tag="column_settings_window"):
            
            dpg.add_text("Pengaturan Kolom untuk Output TXT File", color=(218, 108, 108))
            dpg.add_text("File: [input]_for_qgis_make_sector_NDB.txt", color=(160, 160, 160))
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            dpg.add_text("Daftar kolom yang akan disimpan dalam file TXT output:", color=(234, 235, 208))
            dpg.add_text("Format: Satu kolom per baris atau pisahkan dengan koma", color=(160, 160, 160))
            dpg.add_text("Anda dapat menambahkan kolom custom yang tidak ada dalam daftar preset", color=(160, 160, 160))
            dpg.add_spacer(height=10)
            
            # Text input area for columns
            dpg.add_text("Kolom yang akan disertakan:", color=(234, 235, 208))
            current_columns_text = "\n".join(self.allowed_columns_raw)
            dpg.add_input_text(tag="columns_input_text", width=850, height=300, 
                             multiline=True, default_value=current_columns_text,
                             hint="Masukkan nama kolom, satu per baris...",
                             callback=lambda: self.update_column_count())
            
            dpg.add_spacer(height=15)
            
            # Preset buttons
            dpg.add_text("Preset Kolom:", color=(234, 235, 208))
            with dpg.group(horizontal=True):
                dpg.add_button(label="Load Default", callback=self.load_default_columns)
                dpg.add_button(label="Load Minimal", callback=self.load_minimal_columns)
                dpg.add_button(label="Load Full", callback=self.load_full_columns)
                dpg.add_button(label="Clear All", callback=self.clear_all_columns)
            
            dpg.add_spacer(height=10)
            
            # Reference section - collapsible
            with dpg.collapsing_header(label="[*] Referensi Kolom yang Tersedia", default_open=False):
                dpg.add_text("Kolom-kolom yang umum digunakan (copy-paste ke text area di atas):", color=(160, 160, 160))
                dpg.add_spacer(height=5)
                
                categories = {
                    "[*] Identifikasi Site & Cell": [
                        "SITE_ID", "SiteID", "site_id", "SITE_NAME", "SITE NAME", "SITENAME", 
                        "CELL_ID", "CellID", "cell_id", "CELL_NAME", "CELL", "CELL NAME"
                    ],
                    "[*] Koordinat & Lokasi": [
                        "Longitude", "X_LONGITUDE", "LONG", "LON",
                        "Latitude", "Y_LATITUDE", "LAT"
                    ],
                    "[*] Antenna & RF": [
                        "ANTENNA_TYPE", "AntennaType", "Antenna_Type", "Fixed_Ant_Size", "FixedSize", "AntSize",
                        "ANTENNA_AZIMUTH_DEG", "Azimuth", "AZIMUTH", "HEIGHT_ANTENNA_M", "HEIGHT_ANTENNA", 
                        "ANTENNA_HEIGHT", "HEIGHT", "HORIZONTAL_BEAMWIDTH_DEG", "Beamwidth", "BEAMWIDTH"
                    ],
                    "[*] Sector & System": [
                        "SECTOR_TYPE", "SectorType", "sector_type", "Class_Cell", "ClassCell", 
                        "Cell_Class", "CELL_SYSTEM_INFO"
                    ],
                    "[*] Area & Region": [
                        "CITY_OR_DATI_II", "CITY", "CLUTTER", "AREA", "BRANCH", "PROVINCE", "REGION"
                    ],
                    "[*] Network & Vendor": [
                        "Nano_Cluster", "Cluster", "Nano Cluster", "Vendor", "BTS_VENDOR",
                        "BCCH_OR_TRX1_Freq", "LAC", "PCI", "TAC_4G"
                    ]
                }
                
                for category, columns in categories.items():
                    with dpg.collapsing_header(label=category, default_open=False):
                        columns_text = ", ".join(columns)
                        dpg.add_input_text(default_value=columns_text, readonly=True, width=800)
                        
            dpg.add_spacer(height=15)
            
            # Summary
            dpg.add_text("", tag="column_count_text", color=(218, 108, 108))
            self.update_column_count()
            
            dpg.add_spacer(height=15)
            
            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Simpan", callback=self.save_column_settings)
                dpg.add_button(label="Batal", callback=lambda: dpg.delete_item("column_settings_window"))
                
    def parse_columns_from_text(self, text):
        """Parse columns from text input (supports newline and comma separated)"""
        if not text or not text.strip():
            return []
        
        # Replace newlines with commas first, then split by comma
        text = text.replace('\n', ',').replace('\r', ',')
        columns = [col.strip() for col in text.split(',') if col.strip()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_columns = []
        for col in columns:
            if col not in seen:
                seen.add(col)
                unique_columns.append(col)
                
        return unique_columns
    
    def update_column_count(self):
        """Update column count display"""
        if dpg.does_item_exist("columns_input_text"):
            text = dpg.get_value("columns_input_text")
            columns = self.parse_columns_from_text(text)
            count_text = f"Total kolom: {len(columns)}"
            if len(columns) > 0:
                count_text += f" | Preview: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}"
            dpg.set_value("column_count_text", count_text)
    
    def load_default_columns(self):
        """Load default columns into text area"""
        default_columns = get_default_columns()
        columns_text = "\n".join(default_columns)
        dpg.set_value("columns_input_text", columns_text)
        self.update_column_count()
        
    def load_minimal_columns(self):
        """Load minimal essential columns"""
        minimal_columns = [
            "SITE_ID", "Longitude", "Latitude", "CELL_NAME", "CELL_ID",
            "ANTENNA_AZIMUTH_DEG", "Fixed_Ant_Size", "Class_Cell"
        ]
        columns_text = "\n".join(minimal_columns)
        dpg.set_value("columns_input_text", columns_text)
        self.update_column_count()
        
    def load_full_columns(self):
        """Load all available columns"""
        all_columns = get_default_columns()  # Same as default for now
        columns_text = "\n".join(all_columns)
        dpg.set_value("columns_input_text", columns_text)
        self.update_column_count()
        
    def clear_all_columns(self):
        """Clear all columns from text area"""
        dpg.set_value("columns_input_text", "")
        self.update_column_count()
        

    def save_column_settings(self):
        """Save column settings from text input"""
        if not dpg.does_item_exist("columns_input_text"):
            return
            
        text = dpg.get_value("columns_input_text")
        self.allowed_columns_raw = self.parse_columns_from_text(text)
        
        # Auto save to file
        success = save_column_settings(self.allowed_columns_raw)
        
        if success:
            self.log_message("SETTING", f"Column settings saved: {len(self.allowed_columns_raw)} kolom tersimpan otomatis")
        else:
            self.log_message("WARNING", "Gagal menyimpan setting kolom ke file")
            
        if self.allowed_columns_raw:
            self.log_message("SETTING", f"Kolom terpilih: {', '.join(self.allowed_columns_raw[:5])}{'...' if len(self.allowed_columns_raw) > 5 else ''}")
        
        dpg.delete_item("column_settings_window")

    def show_help(self):
        """Show help information"""
        with dpg.window(label="Help - NDB CSV Processor", modal=True, show=True, 
                       width=750, height=600, pos=(50, 50), tag="help_window"):
            
            dpg.add_text("NDB CSV Processor v2.0.0", color=(218, 108, 108))
            dpg.add_text("Advanced Network Database CSV Processing Tool", color=(160, 160, 160))
            dpg.add_text("GitHub: https://github.com/hadifauzan/ndb-csv-processor", color=(160, 160, 160))
            dpg.add_text("Author: Hadi Fauzan Hanif | © 2024", color=(160, 160, 160))
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            dpg.add_text("[*] CARA PENGGUNAAN:", color=(234, 235, 208))
            dpg.add_text("1. Pilih file CSV input dari folder default atau browse manual")
            dpg.add_text("2. Set output directory (default: Documents/NDB CSV Processor/output)")
            dpg.add_text("3. (Opsional) Set filter Region dan/atau Site ID untuk data subset")
            dpg.add_text("4. (Opsional) Klik 'Setting Kolom' untuk custom kolom TXT output")
            dpg.add_text("5. Klik 'Mulai Proses' untuk memulai transformasi data")
            dpg.add_text("6. Selesai proses → Folder output otomatis terbuka")
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] DEFAULT FOLDERS:", color=(234, 235, 208))
            dpg.add_text(f"Input: {self.default_input_dir}", color=(160, 160, 160))
            dpg.add_text(f"Output: {self.default_output_dir}", color=(160, 160, 160))
            dpg.add_text(f"Settings: Documents/NDB CSV Processor/settings/", color=(160, 160, 160))
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] OUTPUT FILES:", color=(234, 235, 208))
            dpg.add_text("- [input]_for_qgis_make_sector_NDB.txt - Data transformasi untuk QGIS")
            dpg.add_text("- [input]_for_raw_TA_and_audit.csv - File utama untuk TA dan audit (10 kolom)")
            dpg.add_text("- [input]_for_raw_1st_tier.csv - File simple untuk 1st tier (5 kolom)")
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] FITUR UTAMA:", color=(234, 235, 208))
            dpg.add_text("- Transformasi data intelligent dengan algoritma advanced")
            dpg.add_text("- Fixed_Ant_Size mapping berdasarkan teknologi cellular (GSM, LTE, 5G)")
            dpg.add_text("- Class_Cell extraction dari CELL_NAME pattern recognition")
            dpg.add_text("- Sector extraction dari digit terakhir CELL_NAME")
            dpg.add_text("- Filter multi-region dan Site ID dengan OR/AND logic")
            dpg.add_text("- Custom column selector dengan persistent settings")
            dpg.add_text("- Auto file cleanup dan deduplication")
            dpg.add_text("- Real-time progress tracking dan detailed logging")
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] PERFORMANCE & TEKNOLOGI:", color=(234, 235, 208))
            dpg.add_text("- Processing speed: ~1-2 menit untuk 500K+ rows")
            dpg.add_text("- Memory efficient dengan pandas optimizations")
            dpg.add_text("- Multi-threading untuk UI responsiveness")
            dpg.add_text("- Dear PyGui modern interface dengan custom theming")
            dpg.add_text("- Cross-platform compatibility (Windows, Linux, macOS)")
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] SETTING KOLOM ADVANCED:", color=(234, 235, 208))
            dpg.add_text("- Text-based column editor dengan multi-format support")
            dpg.add_text("- 4 preset configurations (Default, Minimal, Full, Clear)")
            dpg.add_text("- Custom column addition diluar preset yang tersedia")
            dpg.add_text("- Real-time validation dan counter dengan preview")
            dpg.add_text("- Auto-save/load settings dengan JSON persistence")
            dpg.add_text("- Kategori referensi kolom yang comprehensive")
            
            dpg.add_spacer(height=10)
            dpg.add_text("[*] TROUBLESHOOTING:", color=(234, 235, 208))
            dpg.add_text("- Pastikan file CSV valid dengan encoding UTF-8")
            dpg.add_text("- Cek write permission di output directory")
            dpg.add_text("- Monitor log window untuk detail error messages")
            dpg.add_text("- Setting file corruption → Auto fallback ke default")
            dpg.add_text("- Large dataset → Tutup aplikasi lain untuk optimasi memory")
            
            dpg.add_spacer(height=15)
            dpg.add_button(label="Tutup", callback=lambda: dpg.delete_item("help_window"))
                
    def update_ui(self):
        """Update UI elements based on current state"""
        try:
            # Update progress bar
            while not self.progress_queue.empty():
                value, text = self.progress_queue.get_nowait()
                dpg.set_value("progress_bar", value / 100.0)
                if text:
                    dpg.set_value("progress_text", text)
                    
            # Update log
            while not self.log_queue.empty():
                log_msg = self.log_queue.get_nowait()
                current_log = dpg.get_value("log_text")
                new_log = current_log + log_msg + "\n"
                # Keep only last 100 lines
                lines = new_log.split('\n')
                if len(lines) > 100:
                    lines = lines[-100:]
                    new_log = '\n'.join(lines)
                dpg.set_value("log_text", new_log)
                
            # Update button states
            if self.is_processing:
                dpg.configure_item("process_button", enabled=False)
                dpg.configure_item("stop_button", enabled=True)
            else:
                dpg.configure_item("process_button", enabled=bool(self.input_file))
                dpg.configure_item("stop_button", enabled=False)
                
        except Exception as e:
            pass
            
    def create_gui(self):
        """Create the main GUI"""
        dpg.create_context()
        
        # Setup theme
        self.setup_theme()
        
        # Main window
        with dpg.window(label="NDB CSV Processor", tag="main_window"):
            # Header
            dpg.add_text("NDB CSV Processor v2.0.0", color=(218, 108, 108))
            dpg.add_text("Advanced Network Database CSV Processing Tool", color=(160, 160, 160))
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Input section
            with dpg.group(label="Input"):
                dpg.add_text("Input CSV File:", color=(234, 235, 208))
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="input_file_text", width=400, readonly=True,
                                     hint="Pilih file CSV...")
                    dpg.add_button(label="Browse", callback=lambda: self.browse_input_file())
                    
            dpg.add_spacer(height=10)
            
            # Output section
            with dpg.group(label="Output"):
                dpg.add_text("Output Directory:", color=(234, 235, 208))
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="output_dir_text", width=400, readonly=True,
                                     default_value=self.output_dir)
                    dpg.add_button(label="Browse", callback=lambda: self.browse_output_dir())
                    
            dpg.add_spacer(height=15)
            
            # Filters section
            with dpg.collapsing_header(label="Filter Options (Opsional)", default_open=False):
                dpg.add_text("Filter berdasarkan REGION:", color=(234, 235, 208))
                
                # Region checkboxes
                with dpg.group():
                    for i, region in enumerate(self.region_options):
                        dpg.add_checkbox(label=region, tag=f"region_{i}",
                                       callback=lambda: self.update_region_filter())
                        
                dpg.add_spacer(height=10)
                dpg.add_text("Filter berdasarkan SITE_ID (pisahkan dengan koma):", color=(234, 235, 208))
                dpg.add_input_text(tag="site_id_filter", width=400, 
                                 hint="Contoh: SITE001,SITE002,SITE003",
                                 callback=lambda s, a: self.update_site_id_filter(s, a))
                                 
            dpg.add_spacer(height=15)
            
            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Mulai Proses", tag="process_button", 
                             callback=lambda: self.process_all_parallel(), enabled=False)
                dpg.add_button(label="Stop", tag="stop_button", 
                             callback=lambda: self.stop_processing(), enabled=False)
                dpg.add_button(label="Setting Kolom", callback=lambda: self.show_column_settings())
                dpg.add_button(label="Lihat Hasil", callback=lambda: self.show_results())
                dpg.add_button(label="Help", callback=lambda: self.show_help())
                
            dpg.add_spacer(height=15)
            
            # Progress section
            dpg.add_text("Progress:", color=(234, 235, 208))
            dpg.add_progress_bar(tag="progress_bar", width=500)
            dpg.add_text("Ready to start...", tag="progress_text", color=(160, 160, 160))
            
            dpg.add_spacer(height=15)
            
            # Log section
            dpg.add_text("Log:", color=(234, 235, 208))
            dpg.add_input_text(tag="log_text", width=600, height=200, 
                             multiline=True, readonly=True, 
                             default_value="NDB CSV Processor ready...\n")
        
        # Error popup
        with dpg.window(label="Error", modal=True, show=False, tag="error_popup",
                       width=400, height=150, pos=(200, 200)):
            dpg.add_text("", tag="error_popup_text", color=(255, 100, 100))
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("error_popup"))
            
    def update_region_filter(self):
        """Update selected regions"""
        self.selected_regions = []
        for i, region in enumerate(self.region_options):
            if dpg.get_value(f"region_{i}"):
                self.selected_regions.append(region)
                
        self.log_message("FILTER", f"Selected regions: {', '.join(self.selected_regions) if self.selected_regions else 'None'}")
        
    def update_site_id_filter(self, sender, app_data):
        """Update site ID filter"""
        self.site_id_filter = app_data
        if self.site_id_filter.strip():
            self.log_message("FILTER", f"Site ID filter: {self.site_id_filter}")
        
    def open_output_folder(self):
        """Open output folder in Windows Explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.output_dir)
            elif os.name == 'posix':  # Linux/Mac
                import subprocess
                subprocess.run(['xdg-open', self.output_dir])
            self.log_message("FOLDER", f"Opened output folder: {self.output_dir}")
        except Exception as e:
            self.log_message("ERROR", f"Failed to open output folder: {str(e)}")

    def run(self):
        """Run the GUI application"""
        self.create_gui()
        
        # Setup viewport without icon
        dpg.create_viewport(title="NDB CSV Processor v2.0.0", width=800, height=800)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        
        # Main loop with UI updates
        while dpg.is_dearpygui_running():
            self.update_ui()
            dpg.render_dearpygui_frame()
            time.sleep(0.016)  # ~60 FPS
            
        dpg.destroy_context()

def main():
    """Main entry point with login handling"""
    try:
        # ========== Login handling ==========
        device_id = get_device_id()
        stored_username, stored_password = read_login_info()
        login_successful = False
        username = None
        
        # Cek jika ada kredensial tersimpan
        if stored_username and stored_password:
            # Auto-login dari registry
            status = check_credentials(stored_username, stored_password, device_id)
            print(f"[DEBUG] Auto-login status untuk {stored_username}: {status}")
            
            if status == "success":
                username = stored_username
                login_successful = True
                print(f"[INFO] Auto-login berhasil untuk user: {username}")
            elif status == "device_mismatch":
                print(f"[WARNING] Auto-login gagal: device mismatch untuk {stored_username}")
                ctypes.windll.user32.MessageBoxW(0, "Username telah terpakai pada device lain", "Login Error", 0)
                sys.exit(0)
            elif status == "invalid_credentials":
                print(f"[WARNING] Kredensial tersimpan tidak valid untuk {stored_username}")
                # Hapus kredensial yang tidak valid dan minta login ulang
                stored_username, stored_password = None, None
        
        # Jika perlu login
        while not login_successful:
            username, password = login_menu()
            if not username or not password:
                print("Login dibatalkan")
                sys.exit(0)
                
            status = check_credentials(username, password, device_id)
            print(f"[DEBUG] Manual-login attempt untuk {username}: {status}")
            
            if status == "success":
                save_login_info(username, password)
                login_successful = True
                print(f"[INFO] Login berhasil untuk user: {username}")
            elif status == "device_mismatch":
                ctypes.windll.user32.MessageBoxW(0, "Username telah terpakai pada device lain", "Login Error", 0)
                sys.exit(0)
            elif status == "invalid_credentials":
                retry = ctypes.windll.user32.MessageBoxW(0, "Username atau password salah.\nCoba lagi?", "Login Error", 0x00000004)  # MB_YESNO
                if retry != 6:  # IDYES = 6
                    print("Login dibatalkan")
                    sys.exit(0)
            else:
                ctypes.windll.user32.MessageBoxW(0, "Terjadi kesalahan saat memeriksa kredensial.", "Login Error", 0)
                sys.exit(0)
        
        if login_successful:
            print(f"[SYSTEM] User {username} berhasil login")
            print("[INFO] Membuka NDB CSV Processor GUI...")
            
            # Jalankan aplikasi GUI setelah login berhasil
            app = NDBProcessorGUI()
            app.run()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 