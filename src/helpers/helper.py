import json
from pathlib import Path
import os

if __name__ == "__main__":
    # 1. Get the Project Root (Go up one level from 'scripts/')
    CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = CURRENT_SCRIPT_DIR.parents[1]
    
    # 2. Define Paths
    # Assumes your json file is named 'data.json' inside the 'data' folder
    source_path = PROJECT_ROOT / "data" / "data.json"
    output_dir = PROJECT_ROOT / "data"
    
    # print("script dir:", CURRENT_SCRIPT_DIR)
    # print("project root:", PROJECT_ROOT)
    # print("exists?", source_path.exists())

    
    # Check if source exists
    if not source_path.exists():
        print(f"Error: Could not find {source_path}")
        exit(1)

    # 3. Load JSON
    with open(source_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 4. Create Files
    # We iterate through the keys (Country Names) and values (Text)
    count = 0
    for country, text in json_data["countries"].items():
        # print(country, type(text['text']))
        text= text['text']
        # break
        # Clean the filename (replace spaces with underscores, lowercase)
        safe_filename = f"{country.strip().lower().replace(' ', '_')}.txt"
        file_path = output_dir / safe_filename
        
        with open(file_path, "w", encoding="utf-8") as out:
            out.write(text)
        
        print(f"Created: {safe_filename}")
        count += 1

    print(f"Success! Extracted {count} country files to {output_dir}")