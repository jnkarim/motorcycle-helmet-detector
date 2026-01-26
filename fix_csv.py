"""
CSV Recovery Tool
Fixes corrupted violations.csv file by removing bad rows
Run with: python fix_csv.py
"""
import csv
import os
from datetime import datetime

CSV_FILE = "violations.csv"
BACKUP_FILE = f"violations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def fix_csv():
    """Fix corrupted CSV by removing invalid rows"""
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ {CSV_FILE} not found!")
        return
    
    # Backup original file
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {BACKUP_FILE}")
    except Exception as e:
        print(f"⚠️ Could not create backup: {e}")
    
    # Read and fix
    valid_rows = []
    invalid_count = 0
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            # Expected header
            expected_header = ["Time", "Plate_Number", "Detection_Confidence", "Source", "Image_File"]
            
            print(f"\n📋 Original file has {len(lines)} lines")
            
            for i, line in enumerate(lines):
                # Keep header
                if i == 0:
                    valid_rows.append(expected_header)
                    continue
                
                try:
                    # Try to parse the line
                    parts = line.strip().split(',')
                    
                    # Expected: Time, Plate_Number, Detection_Confidence, Source, Image_File
                    if len(parts) == 5:
                        valid_rows.append(parts)
                    elif len(parts) > 5:
                        # Too many fields - probably comma in plate number
                        # Try to reconstruct
                        time = parts[0]
                        image_file = parts[-1]
                        source = parts[-2]
                        confidence = parts[-3]
                        # Everything in between is the plate number
                        plate_number = ','.join(parts[1:-3])
                        
                        valid_rows.append([time, plate_number, confidence, source, image_file])
                        print(f"⚠️ Line {i+1}: Fixed extra commas")
                    elif len(parts) < 5:
                        # Too few fields - might be missing data
                        # Pad with empty strings
                        while len(parts) < 5:
                            parts.append('')
                        valid_rows.append(parts)
                        print(f"⚠️ Line {i+1}: Added missing fields")
                    
                except Exception as e:
                    invalid_count += 1
                    print(f"❌ Line {i+1}: Skipped (invalid) - {str(e)[:50]}")
                    continue
        
        # Write fixed CSV
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(valid_rows)
        
        print(f"\n✅ Fixed CSV saved!")
        print(f"   - Valid rows: {len(valid_rows) - 1}")  # -1 for header
        print(f"   - Invalid rows skipped: {invalid_count}")
        print(f"   - Backup saved as: {BACKUP_FILE}")
        
        if invalid_count > 0:
            print(f"\n⚠️ {invalid_count} rows were corrupted and removed")
            print(f"   Check {BACKUP_FILE} if you need to recover data")
        
    except Exception as e:
        print(f"\n❌ Error fixing CSV: {e}")
        print(f"   Restore from backup: {BACKUP_FILE}")

if __name__ == "__main__":
    print("🔧 CSV Recovery Tool")
    print("=" * 50)
    fix_csv()
    print("\n✅ Done! Try running review_violations.py now")