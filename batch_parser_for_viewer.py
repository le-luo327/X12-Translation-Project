#!/usr/bin/env python3
"""
Batch X12 Parser for Claim Viewer
Processes multiple X12 files into section-based format
"""

import os
import sys
import glob
from parser_for_viewer import parse_x12_for_viewer
import json


def batch_parse_for_viewer(input_dir="input_files", output_dir="output_files_viewer"):
    """
    Batch parse all X12 files to viewer format
    """
    print("=" * 70)
    print("Batch X12 Parser for Claim Viewer")
    print("=" * 70)
    print()
    
    # Setup directories
    if not os.path.exists(input_dir):
        print(f"❌ Error: {input_dir} directory not found!")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all X12 files
    extensions = ['*.txt', '*.edi', '*.x12', '*.837', '*.TXT', '*.EDI']
    input_files = []
    
    for ext in extensions:
        pattern = os.path.join(input_dir, ext)
        input_files.extend(glob.glob(pattern))
    
    if not input_files:
        print(f"⚠️  No X12 files found in {input_dir}/")
        print("   Supported extensions: .txt, .edi, .x12, .837")
        return
    
    print(f"📊 Found {len(input_files)} file(s) to process\n")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        filename = os.path.basename(input_file)
        basename_no_ext = os.path.splitext(filename)[0]
        output_file = os.path.join(output_dir, f"{basename_no_ext}_claim.json")
        
        print(f"🔄 Processing: {filename}")
        
        try:
            # Parse to viewer format
            data = parse_x12_for_viewer(input_file)
            
            # Save to JSON
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"   ✅ Parsed → {os.path.basename(output_file)}")
            
            # Count sections/claims
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and 'section' in data[0]:
                    print(f"      {len(data)} sections")
                else:
                    print(f"      {len(data)} claims")
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Failed: {str(e)}")
        
        print()
    
    # Print summary
    print("=" * 70)
    print("Batch Processing Complete")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"\n📁 Output directory: {output_dir}/")
    print("=" * 70)


def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("=" * 70)
            print("Batch X12 Parser for Claim Viewer")
            print("=" * 70)
            print("\nParses multiple X12 files into section-based format")
            print("\nUsage:")
            print("  python3 batch_parser_for_viewer.py [input_dir] [output_dir]")
            print("\nDefault:")
            print("  input_dir='input_files', output_dir='output_files_viewer'")
            print("\nExamples:")
            print("  python3 batch_parser_for_viewer.py")
            print("  python3 batch_parser_for_viewer.py my_input my_claims")
            print("\nOutput Format:")
            print("  Section-based arrays optimized for claim viewer")
            print("  Files named: <input>_claim.json")
            print("=" * 70)
            return
        
        input_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output_files_viewer"
    else:
        input_dir = "input_files"
        output_dir = "output_files_viewer"
    
    batch_parse_for_viewer(input_dir, output_dir)


if __name__ == "__main__":
    main()