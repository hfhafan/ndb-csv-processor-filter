#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main NDB CSV Processor - Console Interface
Integrated script untuk memproses file CSV NDB menjadi berbagai output
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path

def log_message(step, message):
    """Fungsi untuk logging dengan format yang konsisten"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{step}] {message}")

def get_base_filename(file_path):
    """Extract base filename without extension from file path"""
    return Path(file_path).stem

def generate_output_names(input_csv_path):
    """Generate output filenames based on input CSV filename"""
    base_name = get_base_filename(input_csv_path)
    
    output_names = {
        'processed_txt': f"{base_name}_for_qgis_make_sector_NDB.txt",
        'rawndb_csv': f"{base_name}_for_raw_TA_and_audit.csv", 
        'rawndb_simple_csv': f"{base_name}_for_raw_1st_tier.csv"
    }
    
    return output_names

def get_csv_input():
    """Get CSV input file from user"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(current_dir, "Input")
    
    print("\n📁 Pilih input CSV file:")
    print("1. Auto-detect dari folder Input")
    print("2. Input path manual")
    
    choice = input("Pilih opsi (1-2): ").strip()
    
    if choice == "1":
        # Auto-detect CSV file in Input folder
        if os.path.exists(input_dir):
            csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
            if csv_files:
                csv_path = os.path.join(input_dir, csv_files[0])
                log_message("INFO", f"Auto-detected: {csv_files[0]}")
                return csv_path
            else:
                print("❌ Tidak ada file CSV di folder Input!")
                return None
        else:
            print("❌ Folder Input tidak ditemukan!")
            return None
    elif choice == "2":
        csv_path = input("Masukkan path ke file CSV: ").strip().strip('"')
        if os.path.exists(csv_path) and csv_path.lower().endswith('.csv'):
            return csv_path
        else:
            print("❌ File CSV tidak valid atau tidak ditemukan!")
            return None
    else:
        print("❌ Pilihan tidak valid!")
        return None

class NDBDataProcessor:
    """Integrated NDB Data Processor"""
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        # Default allowed columns - can be overridden from GUI
        self.allowed_columns_raw = [
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
        
    def load_data(self):
        """Load CSV data"""
        try:
            log_message("START", "Loading CSV data...")
            start_time = time.time()
            
            # Load with pandas
            self.df = pd.read_csv(self.csv_path, low_memory=False)
            
            load_time = time.time() - start_time
            log_message("SUCCESS", f"Data loaded dalam {load_time:.2f} detik")
            log_message("INFO", f"Shape: {self.df.shape}")
            
            return True
            
        except Exception as e:
            log_message("ERROR", f"Failed to load CSV: {str(e)}")
            return False
    
    def transform_data(self, df):
        """Transform data dengan logic dari Module1.bas"""
        try:
            log_message("START", "Melakukan transformasi data...")
            
            # Copy dataframe
            transformed_df = df.copy()
            
            # 1. Fixed_Ant_Size mapping based on CELL_SYSTEM_INFO (sesuai macro VBA)
            def get_fixed_ant_size(cell_system_info):
                if pd.isna(cell_system_info):
                    return 0.08  # Default dari macro
                
                cell_system_str = str(cell_system_info).upper()
                
                # Mapping sesuai macro VBA
                if cell_system_str.startswith('GSM900'):
                    return 0.03
                elif cell_system_str.startswith('LTE1800'):
                    return 0.095
                elif cell_system_str.startswith('LTE2100'):
                    return 0.085  # Berbeda dari sebelumnya
                elif cell_system_str.startswith('LTE900'):
                    return 0.1    # Berbeda dari sebelumnya
                elif cell_system_str.startswith('DCS1800'):
                    return 0.02   # Baru ditambahkan
                elif cell_system_str.startswith('5G18'):
                    return 0.07   # Berbeda dari sebelumnya
                elif cell_system_str.startswith('5G21'):
                    return 0.065  # Berbeda dari sebelumnya
                elif cell_system_str.startswith('5G_26G'):
                    return 0.065  # Baru ditambahkan
                elif cell_system_str.startswith('L18'):
                    return 0.09   # Baru ditambahkan
                elif cell_system_str.startswith('L21'):
                    return 0.08   # Baru ditambahkan
                else:
                    return 0.08   # Default dari macro
            
            # Apply Fixed_Ant_Size
            if 'CELL_SYSTEM_INFO' in transformed_df.columns:
                transformed_df.loc[:, 'Fixed_Ant_Size'] = transformed_df['CELL_SYSTEM_INFO'].apply(get_fixed_ant_size)
            else:
                transformed_df.loc[:, 'Fixed_Ant_Size'] = 0.03
            
            # 2. Class_Cell extraction from CELL_NAME (sesuai macro VBA)
            def extract_class_cell(cell_name):
                if pd.isna(cell_name):
                    return ""
                
                cell_name_str = str(cell_name).upper()
                
                # Cari pattern sesuai macro VBA: ambil 3 karakter setelah prefix jika dimulai A/B/C/D
                prefixes = ['L18_', 'L21_', '5G18_', '5G21_']
                
                for prefix in prefixes:
                    pos = cell_name_str.find(prefix)
                    if pos >= 0:
                        # Ambil 3 karakter setelah prefix
                        start_pos = pos + len(prefix)
                        if start_pos < len(cell_name_str):
                            sub_part = cell_name_str[start_pos:start_pos + 3]
                            # Cek apakah karakter pertama adalah A/B/C/D
                            if len(sub_part) > 0 and sub_part[0] in 'ABCD':
                                return prefix + sub_part
                
                # If no pattern with letter A/B/C/D found, return blank
                return ""
            
            # Apply Class_Cell
            if 'CELL_NAME' in transformed_df.columns:
                transformed_df.loc[:, 'Class_Cell'] = transformed_df['CELL_NAME'].apply(extract_class_cell)
            else:
                transformed_df.loc[:, 'Class_Cell'] = ""
            
            # 3. INDOOR site handling - divide antenna size by 4 (sesuai macro VBA)
            # Cek kolom SITE_TYPE_GF_OR_RT_OR_MICROCELL_OR_INDOOR dulu, fallback ke SITE_NAME
            indoor_col = None
            if 'SITE_TYPE_GF_OR_RT_OR_MICROCELL_OR_INDOOR' in transformed_df.columns:
                indoor_col = 'SITE_TYPE_GF_OR_RT_OR_MICROCELL_OR_INDOOR'
                indoor_mask = transformed_df[indoor_col] == 'INDOOR'
            elif 'SITE_NAME' in transformed_df.columns:
                indoor_col = 'SITE_NAME'
                indoor_mask = transformed_df[indoor_col].str.contains('INDOOR', case=False, na=False)
            
            if indoor_col is not None:
                transformed_df.loc[indoor_mask, 'Fixed_Ant_Size'] = transformed_df.loc[indoor_mask, 'Fixed_Ant_Size'] / 4
            
            log_message("SUCCESS", "Transformasi data selesai")
            return transformed_df
            
        except Exception as e:
            log_message("ERROR", f"Transformation failed: {str(e)}")
            raise
    
    def filter_allowed_columns(self, df):
        """Filter kolom yang diperbolehkan (dapat dikustomisasi dari GUI)"""
        try:
            log_message("START", "Filtering kolom yang diperbolehkan...")
            log_message("INFO", f"Using custom allowed columns: {len(self.allowed_columns_raw)} kolom")
            
            # CATATAN: SECTORID/SectorID/Sector tidak disertakan dalam allowed columns
            # karena kita akan generate Sector sendiri dari regex extraction CELL_NAME
            
            # Convert to uppercase for comparison
            allowed_columns_upper = [col.upper() for col in self.allowed_columns_raw]
            
            # Filter columns that exist in dataframe
            existing_columns = []
            for col in df.columns:
                if col.upper() in allowed_columns_upper:
                    existing_columns.append(col)
            
            filtered_df = df[existing_columns].copy()
            
            log_message("INFO", f"Kolom yang dipertahankan: {len(existing_columns)} dari {len(df.columns)}")
            log_message("SUCCESS", "Filtering kolom selesai")
            
            return filtered_df
            
        except Exception as e:
            log_message("ERROR", f"Column filtering failed: {str(e)}")
            raise

class FinalOutputGenerator:
    """Generate final output files"""
    
    def __init__(self, processed_data_path):
        self.processed_data_path = processed_data_path
        self.df = None
        
    def load_processed_data(self):
        """Load processed data"""
        try:
            log_message("START", f"Loading processed data dari {self.processed_data_path}...")
            start_time = time.time()
            
            self.df = pd.read_csv(self.processed_data_path, sep='\t', low_memory=False)
            
            load_time = time.time() - start_time
            log_message("SUCCESS", f"Data loaded dalam {load_time:.2f} detik")
            log_message("INFO", f"Shape: {self.df.shape}")
            log_message("INFO", f"Kolom: {list(self.df.columns)}")
            
            return True
            
        except Exception as e:
            log_message("ERROR", f"Failed to load processed data: {str(e)}")
            return False
    
    def generate_rawndb_csv(self, output_name):
        """Generate RAWNDB.csv output"""
        try:
            log_message("START", f"Membuat output {output_name}...")
            
            # Column mapping
            column_mapping = {
                'SITE_ID': 'Site ID',
                'X_LONGITUDE': 'Longitude', 
                'Y_LATITUDE': 'Latitude',
                'ANTENNA_AZIMUTH_DEG': 'Dir',
                'HORIZONTAL_BEAMWIDTH_DEG': 'Ant_BW',
                'Fixed_Ant_Size': 'Ant Size',
                'CELL_NAME': 'EUtranCell',
                'CELL_ID': 'cellId',
                'Class_Cell': 'Class_Cell'
            }
            
            # Select and rename columns
            available_columns = {k: v for k, v in column_mapping.items() if k in self.df.columns}
            output_df = self.df[list(available_columns.keys())].copy()
            output_df.rename(columns=available_columns, inplace=True)
            
            log_message("INFO", f"Kolom setelah rename: {list(output_df.columns)}")
            
            # Generate Sector column dari CELL_NAME (EUtranCell) menggunakan regex extraction
            # TIDAK menggunakan kolom SECTORID/SectorID yang sudah ada di input CSV
            # Ambil HANYA 1 digit terakhir saja (bukan semua digit)
            if 'EUtranCell' in output_df.columns:
                log_message("INFO", "Generating Sector column dari 1 digit terakhir CELL_NAME...")
                sector_values = output_df['EUtranCell'].str.extract(r'(\d)$')
                output_df.loc[:, 'Sector'] = pd.to_numeric(sector_values[0], errors='coerce')
                log_message("INFO", "Sector extraction complete - mengambil 1 digit terakhir dari CELL_NAME.")
            else:
                log_message("WARNING", "EUtranCell (CELL_NAME) column not found. Sector akan diisi dengan NaN.")
                output_df.loc[:, 'Sector'] = pd.NA
            
            # Reorder columns to match required header order
            # Site ID,Longitude,Latitude,Dir,Ant_BW,Ant Size,Sector,EUtranCell,cellId,Class_Cell
            desired_order = ['Site ID', 'Longitude', 'Latitude', 'Dir', 'Ant_BW', 'Ant Size', 'Sector', 'EUtranCell', 'cellId', 'Class_Cell']
            existing_order = [col for col in desired_order if col in output_df.columns]
            output_df = output_df[existing_order]
            
            # Filter out rows with Site ID starting with '0'
            if 'Site ID' in output_df.columns:
                exclude_prefixes = ['0']
                log_message("INFO", f"Excluding rows dengan Site ID prefix: {exclude_prefixes}")
                
                log_message("START", "Filtering rows by Site ID prefixes...")
                initial_count = len(output_df)
                
                for prefix in exclude_prefixes:
                    output_df = output_df[~output_df['Site ID'].astype(str).str.startswith(prefix)]
                
                final_count = len(output_df)
                log_message("INFO", f"Filtered: {initial_count:,} -> {final_count:,} rows")
            
            # Validate numeric columns
            log_message("START", "Validating numeric columns...")
            numeric_columns = ['Longitude', 'Latitude', 'Dir', 'Ant_BW', 'Ant Size', 'cellId', 'Sector']
            
            for col in numeric_columns:
                if col in output_df.columns:
                    output_df.loc[:, col] = pd.to_numeric(output_df[col], errors='coerce')
            
            # Remove rows with invalid coordinates
            if 'Longitude' in output_df.columns and 'Latitude' in output_df.columns:
                output_df = output_df.dropna(subset=['Longitude', 'Latitude'])
            
            log_message("SUCCESS", f"Validation complete. Final rows: {len(output_df):,}")
            
            # Save file
            log_message("START", f"Saving {output_name}...")
            output_df.to_csv(output_name, index=False)
            
            # File info
            file_size = os.path.getsize(output_name) / (1024 * 1024)
            log_message("SUCCESS", f"{output_name} tersimpan: {os.path.abspath(output_name)}")
            log_message("INFO", f"Ukuran file: {file_size:.2f} MB")
            log_message("INFO", f"Jumlah baris: {len(output_df):,}")
            log_message("INFO", f"Jumlah kolom: {len(output_df.columns)}")
            
            return True
            
        except Exception as e:
            log_message("ERROR", f"Failed to generate {output_name}: {str(e)}")
            return False
    
    def generate_rawndb_simple_csv(self, output_name):
        """Generate RAWNDB_simple.csv output"""
        try:
            log_message("START", f"Membuat output {output_name}...")
            
            # Required columns for simple output
            required_columns = ['Site ID', 'Longitude', 'Latitude', 'Dir', 'Sector']
            
            # Check if we have the required columns from previous step
            temp_df = pd.read_csv(output_name.replace('_for_raw_1st_tier.csv', '_for_raw_TA_and_audit.csv'))
            
            # Create subset
            available_columns = [col for col in required_columns if col in temp_df.columns]
            simple_df = temp_df[available_columns].copy()
            
            log_message("INFO", f"Subset created dengan kolom: {available_columns}")
            
            # Remove duplicates
            initial_count = len(simple_df)
            simple_df = simple_df.drop_duplicates()
            final_count = len(simple_df)
            
            log_message("INFO", f"Removed duplicates: {initial_count:,} -> {final_count:,} rows")
            
            # Save file
            log_message("START", f"Saving {output_name}...")
            simple_df.to_csv(output_name, index=False)
            
            # File info
            file_size = os.path.getsize(output_name) / (1024 * 1024)
            log_message("SUCCESS", f"{output_name} tersimpan: {os.path.abspath(output_name)}")
            log_message("INFO", f"Ukuran file: {file_size:.2f} MB")
            log_message("INFO", f"Jumlah baris: {len(simple_df):,}")
            log_message("INFO", f"Jumlah kolom: {len(simple_df.columns)}")
            
            return True
            
        except Exception as e:
            log_message("ERROR", f"Failed to generate {output_name}: {str(e)}")
            return False
    
    def generate_final_outputs(self, output_names):
        """Generate all final outputs"""
        try:
            if not self.load_processed_data():
                return False
            
            # Generate RAWNDB.csv
            if not self.generate_rawndb_csv(output_names['rawndb_csv']):
                return False
            
            # Generate RAWNDB_simple.csv
            if not self.generate_rawndb_simple_csv(output_names['rawndb_simple_csv']):
                return False
            
            return True
            
        except Exception as e:
            log_message("ERROR", f"Final outputs generation failed: {str(e)}")
            return False

def process_step2(csv_path, output_names):
    """
    Step 2: Transform dan filter data CSV
    """
    try:
        log_message("STEP2", "=== Data Transformation ===")
        
        # Create processor instance
        processor = NDBDataProcessor(csv_path)
        
        # Load data
        if not processor.load_data():
            raise Exception("Failed to load CSV data")
        
        # Transform data
        log_message("STEP2", "Transforming data...")
        transformed_df = processor.transform_data(processor.df)
        
        # Filter columns
        log_message("STEP2", "Filtering allowed columns...")
        final_df = processor.filter_allowed_columns(transformed_df)
        
        # Save processed data
        output_file = output_names['processed_txt']
        final_df.to_csv(output_file, sep='\t', index=False)
        
        log_message("COMPLETE", f"Step 2 completed: {output_file}")
        log_message("INFO", f"Final shape: {final_df.shape}")
        log_message("INFO", f"Kolom yang dipertahankan: {len(final_df.columns)}")
        
        return True
        
    except Exception as e:
        log_message("ERROR", f"Step 2 failed: {str(e)}")
        return False

def process_step4(output_names):
    """
    Step 4: Generate final outputs (RAWNDB files)
    """
    try:
        log_message("STEP4", "=== Final Outputs Generator ===")
        
        # Check if processed data exists
        processed_file = output_names['processed_txt']
        if not os.path.exists(processed_file):
            raise Exception(f"{processed_file} not found. Run Step 2 first.")
        
        # Generate final outputs
        generator = FinalOutputGenerator(processed_file)
        
        if generator.generate_final_outputs(output_names):
            log_message("COMPLETE", "Step 4 completed successfully!")
            
            # Show results
            log_message("RESULTS", "Generated files:")
            for key, filename in output_names.items():
                if key != 'processed_txt' and os.path.exists(filename):
                    size_mb = os.path.getsize(filename) / (1024 * 1024)
                    log_message("INFO", f"- {filename}: {size_mb:.1f} MB")
            
            return True
        else:
            raise Exception("Failed to generate final outputs")
            
    except Exception as e:
        log_message("ERROR", f"Step 4 failed: {str(e)}")
        return False

def process_all_steps(csv_path):
    """
    Run all processing steps
    """
    try:
        log_message("START", "=== NDB CSV Processing Started ===")
        log_message("INPUT", f"CSV File: {csv_path}")
        
        # Generate output names based on input
        output_names = generate_output_names(csv_path)
        log_message("INFO", f"Output files akan dibuat:")
        for key, name in output_names.items():
            log_message("INFO", f"- {name}")
        
        overall_start = time.time()
        
        # Step 2: Transform data
        step2_start = time.time()
        if not process_step2(csv_path, output_names):
            return False
        step2_time = time.time() - step2_start
        log_message("TIMING", f"Step 2 took {step2_time:.2f} seconds")
        
        # Step 4: Generate final outputs
        step4_start = time.time()
        if not process_step4(output_names):
            return False
        step4_time = time.time() - step4_start
        log_message("TIMING", f"Step 4 took {step4_time:.2f} seconds")
        
        # Summary
        total_time = time.time() - overall_start
        log_message("COMPLETE", f"=== ALL PROCESSING COMPLETED ===")
        log_message("TIMING", f"Total processing time: {total_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        log_message("ERROR", f"Processing failed: {str(e)}")
        return False

def main():
    """Main console interface"""
    try:
        print("🚀 Selamat datang di NDB CSV Processor!")
        print("Script ini akan memproses file CSV menjadi 3 output file")
        print("=" * 60)
        print("           MAIN NDB CSV PROCESSOR")
        print("=" * 60)
        print("1. Jalankan semua proses")
        print("2. Hanya transform data (Step 2)")
        print("3. Hanya generate outputs (Step 4)")
        print("4. Keluar")
        print("=" * 60)
        print("Output files akan dinamai berdasarkan input file:")
        print("- [input]_for_qgis_make_sector_NDB.txt")
        print("- [input]_for_raw_TA_and_audit.csv")
        print("- [input]_for_raw_1st_tier.csv")
        
        choice = input("Pilih opsi (1-4): ").strip()
        
        if choice == "1":
            # Run all steps
            csv_path = get_csv_input()
            if csv_path:
                return process_all_steps(csv_path)
        
        elif choice == "2":
            # Only Step 2
            csv_path = get_csv_input()
            if csv_path:
                output_names = generate_output_names(csv_path)
                return process_step2(csv_path, output_names)
        
        elif choice == "3":
            # Only Step 4
            csv_path = get_csv_input()
            if csv_path:
                output_names = generate_output_names(csv_path)
                return process_step4(output_names)
        
        elif choice == "4":
            print("👋 Sampai jumpa!")
            return True
        
        else:
            print("❌ Pilihan tidak valid!")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Proses dihentikan oleh user")
        return False
    
    except Exception as e:
        log_message("ERROR", f"Main process failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        if main():
            print("\n✅ Program selesai dengan sukses!")
        else:
            print("\n❌ Program selesai dengan error!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)