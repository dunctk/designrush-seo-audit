#!/usr/bin/env python3
"""Capture homepage screenshot and update presentation."""

import subprocess
import json
import base64
import time
from pathlib import Path

def run_command(cmd, description, timeout=300):
    """Run a command with timeout."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timed out")
        return False

def extract_screenshot_from_json(json_path):
    """Extract screenshot from JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if 'content' in data and data['content']:
            # Fix URL-safe base64 characters and padding
            content = data['content'].replace('-', '+').replace('_', '/')
            padding_needed = 4 - (len(content) % 4)
            if padding_needed != 4:
                content += '=' * padding_needed
            
            # Decode base64 image data
            image_data = base64.b64decode(content)
            
            # Create PNG filename
            png_path = json_path.with_suffix('.png')
            
            # Write image data
            with open(png_path, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ Extracted screenshot: {png_path}")
            print(f"   Size: {len(image_data)} bytes")
            return True
        else:
            print(f"❌ No image data found in {json_path}")
            return False
    except Exception as e:
        print(f"❌ Error extracting screenshot: {e}")
        return False

def main():
    print("🚀 Starting homepage screenshot capture and presentation update...")
    
    # Step 1: Create homepage target file
    homepage_yml = Path("homepage_temp.yml")
    homepage_yml.write_text("""---
- name: 01-homepage
  url: https://www.designrush.com/
  devices: [desktop]""")
    print("✅ Created homepage target file")
    
    # Step 2: Capture screenshot
    capture_cmd = f"PYTHONPATH=/Users/dunc/Documents/Code/designrush-seo-audit/src uv run python scripts/capture_screenshots.py --targets {homepage_yml} --out-dir artifacts/2025-09-12/screenshots"
    
    success = run_command(capture_cmd, "Capturing homepage screenshot", timeout=180)
    
    if not success:
        print("❌ Screenshot capture failed or timed out")
        homepage_yml.unlink()  # Clean up
        return
    
    # Step 3: Check for JSON file and extract
    screenshots_dir = Path("artifacts/2025-09-12/screenshots")
    homepage_json = screenshots_dir / "01-homepage__desktop.json"
    
    if homepage_json.exists():
        print("✅ Found homepage JSON file")
        if extract_screenshot_from_json(homepage_json):
            print("✅ Successfully extracted homepage screenshot")
        else:
            print("❌ Failed to extract homepage screenshot")
            homepage_yml.unlink()
            return
    else:
        print("❌ Homepage JSON file not found")
        homepage_yml.unlink()
        return
    
    # Step 4: Regenerate presentation
    regen_cmd = "PYTHONPATH=/Users/dunc/Documents/Code/designrush-seo-audit/src uv run python scripts/analyze_positions.py --csv data/www.designrush.com_agency-organic.Positions-us-20250911-2025-09-12T16_10_02Z.csv"
    
    if run_command(regen_cmd, "Regenerating presentation", timeout=300):
        print("🎉 Success! Homepage screenshot added to presentation")
        print("📖 View updated presentation at: http://localhost:8000/deck.html")
    else:
        print("❌ Failed to regenerate presentation")
    
    # Clean up
    homepage_yml.unlink()
    print("🧹 Cleaned up temporary files")

if __name__ == "__main__":
    main()