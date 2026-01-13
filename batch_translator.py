#!/usr/bin/env python3
"""
Batch X12 to JSON Translator with Complete Structured Output
Processes multiple X12 files with validation
ENHANCED: Shows detected file types in summary
"""

import os
import sys
import glob
import json

from x12_claims_parser import translate_x12_complete_structured, validate_output


def batch_translate(input_dir="input_files", output_dir="output_files"):
    """
    Batch translate all X12 files to structured JSON with validation
    """
    print("=" * 70)
    print("X12 Batch Translator - Complete Structured Output")
    print("=" * 70)
    print()
    
    if not os.path.exists(input_dir):
        print(f"❌ Error: {input_dir} directory not found!")
        os.makedirs(input_dir)
        print(f"   Created {input_dir}/ - please add X12 files")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    success_count = 0
    error_count = 0
    results = []
    
    for input_file in input_files:
        filename = os.path.basename(input_file)
        basename_no_ext = os.path.splitext(filename)[0]
        output_file = os.path.join(output_dir, f"{basename_no_ext}_parsed.json")
        
        print(f"🔄 Processing: {filename}")
        
        try:
            print(f"   📝 Translating to structured format...")
            data = translate_x12_complete_structured(input_file)
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            summary = data.get('summary', {})
            segments = summary.get('total_segments', 0)
            claims = summary.get('total_claims', 0)
            service_lines = summary.get('total_service_lines', 0)
            
            file_type = data.get('file_info', {}).get('file_type', 'Unknown')
            
            print(f"   ✅ Translated → {os.path.basename(output_file)}")
            print(f"      File Type: {file_type}")
            print(f"      {segments} segments, {claims} claim(s), {service_lines} service line(s)")
            
            print(f"   🔍 Validating...")
            
            try:
                with open(output_file, 'r') as f:
                    json.load(f)
                syntax_valid = True
            except json.JSONDecodeError as e:
                syntax_valid = False
                print(f"      ⚠️  JSON syntax error: {e}")
            
            is_valid, msg = validate_output(data)
            
            if syntax_valid and is_valid:
                print(f"   ✅ Validation passed")
                validation_status = "VALID"
            else:
                print(f"   ⚠️  Validation warning: {msg if not is_valid else 'Syntax error'}")
                validation_status = f"WARNING: {msg if not is_valid else 'Syntax error'}"
            
            size = os.path.getsize(output_file)
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            
            success_count += 1
            results.append({
                'input': filename,
                'output': os.path.basename(output_file),
                'status': 'SUCCESS',
                'validation': validation_status,
                'file_type': file_type,
                'segments': segments,
                'claims': claims,
                'service_lines': service_lines,
                'size': size_str
            })
            
        except Exception as e:
            error_count += 1
            results.append({
                'input': filename,
                'output': '-',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"   ❌ Failed: {str(e)}")
        
        print()
    
    print("=" * 70)
    print("Batch Processing Complete")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    print()
    
    if success_count > 0:
        print("📋 Successful Translations:")
        print()
        for result in results:
            if result['status'] == 'SUCCESS':
                val_icon = "✅" if result['validation'] == "VALID" else "⚠️"
                print(f"  📄 {result['input']}")
                print(f"     → {result['output']}")
                print(f"     → Type: {result['file_type']}")
                print(f"     → {result['segments']} segments, {result['claims']} claims, {result['service_lines']} lines")
                print(f"     → {result['size']}")
                print(f"     {val_icon} {result['validation']}")
                print()
    
    if error_count > 0:
        print("❌ Failed Files:")
        print()
        for result in results:
            if result['status'] == 'FAILED':
                print(f"  📄 {result['input']}")
                print(f"     Error: {result.get('error', 'Unknown error')}")
                print()
    
    if success_count > 0:
        total_segments = sum(r['segments'] for r in results if r['status'] == 'SUCCESS')
        total_claims = sum(r['claims'] for r in results if r['status'] == 'SUCCESS')
        total_lines = sum(r['service_lines'] for r in results if r['status'] == 'SUCCESS')
        
        print("📊 Overall Statistics:")
        print(f"   Total segments processed: {total_segments}")
        print(f"   Total claims extracted: {total_claims}")
        print(f"   Total service lines: {total_lines}")
        print()
        
        file_type_counts = {}
        for result in results:
            if result['status'] == 'SUCCESS':
                file_type = result['file_type']
                file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
        
        if file_type_counts:
            print("📋 File Types Processed:")
            for file_type, count in sorted(file_type_counts.items()):
                print(f"   {file_type}: {count} file(s)")
            print()
    
    print(f"📁 Output directory: {output_dir}/")
    print("=" * 70)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("=" * 70)
            print("X12 Batch Translator - Complete Structured Output")
            print("=" * 70)
            print("\nUsage:")
            print("  python3 batch_translator.py [input_dir] [output_dir]")
            print("\nDefault:")
            print("  input_dir='input_files', output_dir='output_files'")
            print("\nExamples:")
            print("  python3 batch_translator.py")
            print("  python3 batch_translator.py my_input my_output")
            print("\nOutput Format:")
            print("  - Structured JSON with business headers")
            print("  - ALL information included (no filtering)")
            print("  - Automatic file type detection")
            print("  - Automatic validation")
            print("  - Files named: <input>_parsed.json")
            print("\nSupported Transaction Types:")
            print("  - 837P (Professional Healthcare Claim)")
            print("  - 837I (Institutional Healthcare Claim)")
            print("  - 837D (Dental Healthcare Claim)")
            print("  - 835 (Healthcare Claim Payment/Advice)")
            print("  - 270/271 (Eligibility Inquiry/Response)")
            print("  - 276/277 (Claim Status Inquiry/Response)")
            print("  - And more...")
            print("=" * 70)
            return
        
        input_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output_files"
    else:
        input_dir = "input_files"
        output_dir = "output_files"
    
    batch_translate(input_dir, output_dir)


if __name__ == "__main__":
    main()