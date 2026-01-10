# X12 Healthcare Claims Translator

A comprehensive Python-based X12 EDI translator that converts healthcare claim files (837P, 837I, 837D) into structured JSON formats for analysis and display.

## Features

### 🎯 Core Capabilities
- **Multiple Output Formats**: Generate both detailed analysis JSON and viewer-optimized JSON
- **Dynamic File Type Detection**: Automatically identifies 837P (Professional), 837I (Institutional), 837D (Dental)
- **Multi-Method Detection**: Uses BHT06 codes, filename patterns, and provider/payer name analysis
- **Comprehensive Data Extraction**: Preserves all X12 segments and elements
- **Batch Processing**: Process multiple files simultaneously with detailed reporting
- **Built-in Validation**: Automatic JSON syntax and structure validation

### 📋 Supported Transaction Types
- **837P** - Professional Healthcare Claims (physician, dentist offices)
- **837I** - Institutional Healthcare Claims (hospitals, facilities)
- **837D** - Dental Healthcare Claims
- **835** - Healthcare Claim Payment/Advice
- **270/271** - Eligibility Inquiry/Response
- **276/277** - Claim Status Inquiry/Response
- And more...

## Installation

### Prerequisites
- Python 3.7+
- PyX12 library

### Setup
```bash
# Clone the repository
git clone https://github.com/le-luo327/X12-Translation-Project.git
cd X12-Translation-Project

# Install dependencies
pip install pyx12 --break-system-packages
```

## Usage

### Single File Translation - Detailed Format

Parse a single X12 file to comprehensive nested JSON:

```bash
python3 x12_claims_parser.py input_files/837d.txt
```

Output: `output_files/837d_parsed.json`

### Batch Translation - Detailed Format

Process all X12 files in the input directory:

```bash
python3 batch_translator.py
```

Output: All files in `output_files/` directory

### Single File Translation - Viewer Format

Parse to section-based format optimized for frontend display:

```bash
python3 parser_for_viewer.py input_files/837d.txt
```

Output: `output_files_viewer/837d_claim.json`

### Batch Translation - Viewer Format

```bash
python3 batch_parser_for_viewer.py
```

Output: All files in `output_files_viewer/` directory

## Output Formats

### Detailed Format (output_files/)
Comprehensive nested JSON structure with all segments preserved:
```json
{
  "file_info": {
    "source_file": "input_files/837d.txt",
    "file_type": "X12 837D Dental Healthcare Claim"
  },
  "interchange_header": {...},
  "functional_group": {...},
  "transaction_set": {...},
  "billing_provider": {...},
  "subscriber": {...},
  "claims": [
    {
      "claim_id": "...",
      "total_charge": "...",
      "diagnosis_codes": {...},
      "service_lines": [...]
    }
  ],
  "all_segments": [...],
  "summary": {
    "total_segments": 150,
    "total_claims": 3,
    "total_service_lines": 8
  }
}
```

**Use Cases:**
- Data analysis and reporting
- System integration
- Debugging and validation
- Complete data preservation

### Viewer Format (output_files_viewer/)
Section-based array format optimized for claim viewers:
```json
[
  { "section": "transaction", "data": {...} },
  { "section": "submitter", "data": {...} },
  { "section": "billing_Provider", "data": {...} },
  { "section": "subscriber", "data": {...} },
  { "section": "claim", "data": {...} },
  { "section": "diagnosis", "data": {...} },
  { "section": "service_Lines", "data": [...] }
]
```

**Use Cases:**
- Frontend claim viewer applications
- User-facing dashboards
- Simplified data display
- Web application integration

## File Type Detection

The parser uses multiple methods to accurately identify 837 subtypes:

1. **Primary Method - BHT06 Field**: Standard claim type code (P/I/D)
2. **Fallback Method 1 - Filename**: Searches for "837d", "837p", "837i" in filename
3. **Fallback Method 2 - Provider Names**: Detects "DENTAL" in provider organization names
4. **Fallback Method 3 - Payer Names**: Detects "DENTAL" in insurance payer names

This multi-layered approach ensures accurate detection even with non-standard X12 files.

## Project Structure

```
X12-Translation-Project/
├── x12_claims_parser.py           # Single file parser (detailed format)
├── batch_translator.py            # Batch parser (detailed format)
├── parser_for_viewer.py           # Single file parser (viewer format)
├── batch_parser_for_viewer.py     # Batch parser (viewer format)
├── input_files/                   # Input X12 files (.txt, .edi, .837)
├── output_files/                  # Detailed JSON outputs
├── output_files_viewer/           # Viewer-optimized JSON outputs
├── README.md                      # This file
└── .gitignore                     # Git ignore rules

```

## Examples

### Example 1: Process Single Dental Claim
```bash
python3 x12_claims_parser.py input_files/837d.txt

# Output:
# ✅ Translation complete!
# 💾 Output: output_files/837d_parsed.json
# 📊 File Type: X12 837D Dental Healthcare Claim
# 📊 Summary:
#    - Total segments: 150
#    - Total claims: 3
#    - Total service lines: 8
```

### Example 2: Batch Process All Files
```bash
python3 batch_translator.py

# Output:
# 📊 Found 20 file(s) to process
# 
# 🔄 Processing: 837d.txt
#    ✅ Translated → 837d_parsed.json
#       File Type: X12 837D Dental Healthcare Claim
#       150 segments, 3 claim(s), 8 service line(s)
# 
# ✅ Successful: 20
# ❌ Failed: 0
# 
# 📋 File Types Processed:
#    X12 837D Dental Healthcare Claim: 8 file(s)
#    X12 837P Professional Healthcare Claim: 10 file(s)
#    X12 837I Institutional Healthcare Claim: 2 file(s)
```

### Example 3: Generate Viewer Format
```bash
python3 parser_for_viewer.py input_files/837d.txt

# Output:
# ✅ Parsing complete!
# 💾 Output: output_files_viewer/837d_claim.json
# 📊 Generated 12 sections
```

## Error Handling

The parser includes comprehensive error handling:

- **Invalid X12 Format**: Clear error messages for malformed files
- **Missing Segments**: Graceful handling of incomplete files
- **Numeric Parsing**: Safe conversion with tilde and invalid value handling
- **File Not Found**: Helpful error messages with file path

## Development

### Key Technologies
- **PyX12**: X12 EDI file parsing
- **Python 3**: Core programming language
- **JSON**: Structured output format

### Code Features
- Safe numeric parsing (handles tildes: `1~` → `1`)
- Multi-method file type detection
- Comprehensive segment extraction
- Validation at multiple levels
- Clean error messages

## Troubleshooting

### Common Issues

**Issue: "File does not begin with 'ISA'"**
- **Cause**: File is not a valid X12 format
- **Solution**: Verify file contains valid X12 data starting with ISA segment

**Issue: "invalid literal for int() with base 10"**
- **Cause**: Older version without safe numeric parsing
- **Solution**: Update to latest version with `safe_int()` and `safe_float()` functions

**Issue: File type shows generic "X12 837 Healthcare Claim"**
- **Cause**: BHT06 field uses non-standard code
- **Solution**: Parser will use filename/provider name detection as fallback

## Contributing

This project was developed for X12 healthcare claims processing. Contributions and suggestions are welcome!

## License

[Specify your license here]

## Contact

- **Developer**: le-luo327
- **Repository**: https://github.com/le-luo327/X12-Translation-Project

## Acknowledgments

- Built using the PyX12 library for X12 EDI parsing
- Developed during EMRTS internship 2025
- Designed for healthcare claims processing and analysis

---

**Last Updated**: January 2026
**Version**: 2.0 (Enhanced with dynamic file type detection and viewer format)