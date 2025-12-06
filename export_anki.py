#!/usr/bin/env python3
"""
Anki Data Export Script
Extracts daily review counts from Anki database and generates JSON for website visualization
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

# CONFIGURATION - UPDATE THESE PATHS
# Windows example: r"C:\Users\YourName\AppData\Roaming\Anki2\User 1\collection.anki2"
# Mac example: Path.home() / "Library/Application Support/Anki2/User 1/collection.anki2"
# Linux example: Path.home() / ".local/share/Anki2/User 1/collection.anki2"

ANKI_DB = Path(r"C:\Users\Stuart\AppData/Roaming/Anki2/Stuart/collection.anki2")  # Windows default
# ANKI_DB = Path.home() / "Library/Application Support/Anki2/User 1/collection.anki2"  # Mac
# ANKI_DB = Path.home() / ".local/share/Anki2/User 1/collection.anki2"  # Linux

# Output location - adjust this to your portfolio website directory
OUTPUT_FILE = Path(r"C:\Users\Stuart\OneDrive\Documents\Personal Projects\portfolio-website\johnson-stuart.github.io\data\anki_data.json")


def find_anki_database():
    """Try to auto-detect Anki database location"""
    possible_paths = [
        Path.home() / "AppData/Roaming/Anki2/User 1/collection.anki2",  # Windows
        Path.home() / "Library/Application Support/Anki2/User 1/collection.anki2",  # Mac
        Path.home() / ".local/share/Anki2/User 1/collection.anki2",  # Linux
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def extract_anki_data(db_path):
    """Extract daily review counts from Anki database"""
    
    if not db_path.exists():
        print(f"❌ Error: Anki database not found at: {db_path}")
        print("\nPlease update the ANKI_DB path in this script.")
        print("To find your database:")
        print("1. Open Anki")
        print("2. Go to Tools > Preferences > Network")
        print("3. Look for your profile location")
        return None
    
    print(f"📖 Reading Anki database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query reviews from the revlog table
        # id in revlog is timestamp in milliseconds since epoch
        # We group by date and count reviews per day
        query = """
        SELECT 
            date(id/1000, 'unixepoch') as review_date,
            COUNT(*) as review_count
        FROM revlog
        GROUP BY review_date
        ORDER BY review_date
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convert to dictionary format: {"2024-01-01": 25, "2024-01-02": 30, ...}
        data = {}
        for date, count in results:
            data[date] = count
        
        conn.close()
        
        print(f"✅ Extracted {len(data)} days of review data")
        
        if data:
            # Show some stats
            total_reviews = sum(data.values())
            avg_reviews = total_reviews / len(data) if data else 0
            first_date = min(data.keys())
            last_date = max(data.keys())
            
            print(f"\n📊 Statistics:")
            print(f"   Total reviews: {total_reviews:,}")
            print(f"   Average per day: {avg_reviews:.1f}")
            print(f"   Date range: {first_date} to {last_date}")
            print(f"   Days with reviews: {len(data)}")
        
        return data
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return None


def save_json(data, output_path):
    """Save data to JSON file"""
    
    if data is None:
        return False
    
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add metadata
    output_data = {
        "updated": datetime.now().isoformat(),
        "total_days": len(data),
        "total_reviews": sum(data.values()),
        "data": data
    }
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    return True


def main():
    print("=" * 60)
    print("Anki Data Export for Portfolio Website")
    print("=" * 60)
    print()
    
    # Try to find database automatically
    db_path = ANKI_DB
    if not db_path.exists():
        print("⚠️  Configured database path not found. Trying auto-detect...")
        auto_path = find_anki_database()
        if auto_path:
            db_path = auto_path
            print(f"✅ Found database: {db_path}")
        else:
            print("\n❌ Could not find Anki database automatically.")
            print("\nPlease edit this script and update the ANKI_DB variable")
            print("with the correct path to your collection.anki2 file.")
            sys.exit(1)
    
    # Extract data
    data = extract_anki_data(db_path)
    
    if data is None:
        print("\n❌ Export failed!")
        sys.exit(1)
    
    # Save to JSON
    if save_json(data, OUTPUT_FILE):
        print("\n✅ Export complete!")
        print("\nNext steps:")
        print("1. Copy the JSON file to your website's data folder")
        print("2. Commit and push to GitHub:")
        print(f"   git add {OUTPUT_FILE.name}")
        print("   git commit -m 'Update Anki stats'")
        print("   git push")
    else:
        print("\n❌ Failed to save JSON file")
        sys.exit(1)


if __name__ == "__main__":
    main()
