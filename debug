"""
Debug script to check actual column names in your CSV files.
Run this from your project root directory:
    python debug_columns.py
"""

import pandas as pd
from pathlib import Path

def check_columns():
    data_dir = Path('./data')
    
    print("=" * 60)
    print("CHECKING CSV COLUMN NAMES")
    print("=" * 60)
    
    # Check ecocrop file
    ecocrop_file = data_dir / 'cleaned_ecocrop.csv'
    if ecocrop_file.exists():
        print(f"\n✅ Found: {ecocrop_file}")
        df = pd.read_csv(ecocrop_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {df.columns.tolist()}")
        print(f"\n   Sample row:")
        print(df.iloc[0].to_dict())
    else:
        print(f"\n❌ Not found: {ecocrop_file}")
    
    # Check weather file
    weather_file = data_dir / 'merged_aez_weather.csv'
    if weather_file.exists():
        print(f"\n✅ Found: {weather_file}")
        df = pd.read_csv(weather_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {df.columns.tolist()}")
        print(f"\n   Unique AEZ values:")
        if 'aez' in df.columns:
            print(f"   {df['aez'].unique().tolist()}")
        elif 'AEZ' in df.columns:
            print(f"   {df['AEZ'].unique().tolist()}")
        else:
            print("   ⚠️  No 'aez' or 'AEZ' column found!")
            for col in df.columns:
                if 'aez' in col.lower() or 'zone' in col.lower():
                    print(f"   Possible AEZ column: {col}")
                    print(f"   Values: {df[col].unique().tolist()}")
        print(f"\n   Sample row:")
        print(df.iloc[0].to_dict())
    else:
        print(f"\n❌ Not found: {weather_file}")
    
    print("\n" + "=" * 60)
    print("EXPECTED COLUMN NAMES (lowercase)")
    print("=" * 60)
    
    print("\nEcocrop columns needed:")
    print("  - comname (crop common name)")
    print("  - scientificname")
    print("  - tmin, tmax (absolute temperature range)")
    print("  - topmn, topmx (optimal temperature range)")
    print("  - rmin, rmax (absolute rainfall range)")
    print("  - ropmn, ropmx (optimal rainfall range)")
    print("  - phopmn, phopmx (pH range)")
    print("  - gmin, gmax (growth duration in days)")
    
    print("\nWeather columns needed:")
    print("  - date")
    print("  - aez (Agro-Ecological Zone)")
    print("  - prectotcorr (precipitation)")
    print("  - t2m (temperature)")
    print("  - rh2m (relative humidity)")
    print("  - allsky_sfc_sw_dwn (solar radiation)")

if __name__ == "__main__":
    check_columns()
