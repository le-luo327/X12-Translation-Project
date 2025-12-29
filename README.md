# X12 837P to JSON Translator

A Python tool for translating X12 837P healthcare claims EDI files to structured JSON format using the PyX12 library.

## Features

✅ **Complete structured translation** - Organized JSON with business headers
✅ **All information preserved** - No data filtering
✅ **Automatic validation** - Built-in JSON validation
✅ **Batch processing** - Process multiple files at once
✅ **PyX12 library** - Industry-standard X12 parser

## Requirements

- Python 3.8+
- PyX12 library

## Installation
```bash
# Clone the repository
git clone https://github.com/le-luo327/X12-Translation-Project.git
cd X12-Translation-Project

# Install dependencies
pip install pyx12
```

## Usage

### Single File Translation
```bash
python3 x12_claims_parser.py input_files/your_file.txt
```

Output: `output_files/your_file_parsed.json`

### Batch Processing
```bash
python3 batch_translator.py
```

Processes all X12 files in `input_files/` directory.

## Output Format

Structured JSON with complete information:
```json
{
  "file_info": {...},
  "interchange_header": {...},
  "billing_provider": {...},
  "subscriber": {...},
  "claims": [
    {
      "claim_id": "26463774",
      "total_charge": "100",
      "service_lines": [...]
    }
  ],
  "all_segments": [...],
  "summary": {
    "total_segments": 46,
    "total_claims": 1,
    "total_service_lines": 4
  }
}
```

## Project Structure
```
X12-Translation-Project/
├── x12_claims_parser.py      # Main translator
├── batch_translator.py       # Batch processor
├── README.md                 # Documentation
├── .gitignore               # Git ignore rules
├── input_files/             # Input X12 files
└── output_files/            # Generated JSON files
```

## File Naming

- Input: `claim_file.txt` → Output: `claim_file_parsed.json`

## Examples
```bash
# Translate single file
python3 x12_claims_parser.py input_files/X12-837.txt

# Batch process all files
python3 batch_translator.py

# View output
cat output_files/X12-837_parsed.json
```

## Validation

All outputs are automatically validated for:
- JSON syntax correctness
- Required data structures
- Segment completeness

## Author

Le Luo

## Date

December 2025

## License

MIT License