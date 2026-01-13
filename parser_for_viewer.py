#!/usr/bin/env python3
"""
X12 Parser for Claim Viewer
Outputs section-based array format optimized for frontend display
"""

import json
import sys
import os
from pyx12.x12file import X12Reader


def parse_date(date_str):
    """Convert YYYYMMDD to YYYY-MM-DD"""
    if not date_str or len(date_str) != 8:
        return date_str
    try:
        return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except:
        return date_str


def parse_time(time_str):
    """Convert HHMM to HH:MM"""
    if not time_str or len(time_str) < 4:
        return time_str
    try:
        return f"{time_str[0:2]}:{time_str[2:4]}"
    except:
        return time_str


def clean_value(value):
    """Remove tilde, whitespace, and segment terminators from X12 values"""
    if not value:
        return ""
    return str(value).replace('~', '').strip()


def clean_code(code):
    """Remove qualifier prefix from codes (e.g., 'ABK:K0230' -> 'K0230')"""
    if not code:
        return ""
    cleaned = clean_value(code)
    return cleaned.split(":")[-1] if ":" in cleaned else cleaned


def safe_int(value, default=0):
    """Safely convert string to int, handling tildes and invalid values"""
    if not value:
        return default
    try:
        cleaned = clean_value(value)
        return int(cleaned) if cleaned else default
    except (ValueError, AttributeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert string to float, handling tildes and invalid values"""
    if not value:
        return default
    try:
        cleaned = clean_value(value)
        return float(cleaned) if cleaned else default
    except (ValueError, AttributeError):
        return default


def parse_x12_for_viewer(filepath):
    """
    Parse X12 file into section-based format for claim viewer
    Returns array of section objects
    """
    
    # Storage for parsed data
    transaction = {}
    submitter = {}
    receiver = {}
    billing_provider = {}
    pay_to_provider = {}
    subscriber = {}
    payer = {}
    current_claim = None
    claims_data = []
    
    # Temporary storage
    temp_addresses = {}
    temp_demographics = {}
    temp_contacts = {}
    current_entity = None
    
    try:
        with open(filepath, 'r') as f:
            reader = X12Reader(f)
            
            for segment in reader:
                seg_id = segment.get_seg_id()
                seg_str = str(segment)
                elements = seg_str.split('*')
                
                # ISA - Interchange Control Header
                if seg_id == 'ISA':
                    receiver['name'] = clean_value(elements[8] if len(elements) > 8 else "")
                    receiver['id'] = clean_value(elements[8] if len(elements) > 8 else "")
                    submitter['name'] = clean_value(elements[6] if len(elements) > 6 else "")
                
                # ST - Transaction Set Header
                elif seg_id == 'ST':
                    transaction['type'] = clean_value(elements[1] if len(elements) > 1 else "")
                    transaction['controlNumber'] = clean_value(elements[2] if len(elements) > 2 else "")
                    transaction['version'] = clean_value(elements[3] if len(elements) > 3 else "")
                
                # BHT - Beginning of Hierarchical Transaction
                elif seg_id == 'BHT':
                    transaction['purpose'] = clean_value(elements[1] if len(elements) > 1 else "")
                    transaction['referenceId'] = clean_value(elements[3] if len(elements) > 3 else "")
                    transaction['date'] = parse_date(clean_value(elements[4] if len(elements) > 4 else ""))
                    transaction['time'] = parse_time(clean_value(elements[5] if len(elements) > 5 else ""))
                
                # NM1 - Name/Entity
                elif seg_id == 'NM1':
                    entity_code = clean_value(elements[1] if len(elements) > 1 else "")
                    
                    entity_data = {
                        'name': clean_value(elements[3] if len(elements) > 3 else ""),
                        'firstName': clean_value(elements[4] if len(elements) > 4 else ""),
                        'lastName': clean_value(elements[3] if len(elements) > 3 else ""),
                        'id': clean_value(elements[9] if len(elements) > 9 else ""),
                        'idQualifier': clean_value(elements[8] if len(elements) > 8 else "")
                    }
                    
                    if entity_code == '41':  # Submitter
                        current_entity = 'submitter'
                        submitter['name'] = entity_data['name']
                        submitter['id'] = entity_data['id']
                    
                    elif entity_code == '40':  # Receiver
                        current_entity = 'receiver'
                        receiver['name'] = entity_data['name']
                        receiver['id'] = entity_data['id']
                    
                    elif entity_code == '85':  # Billing Provider
                        current_entity = 'billing_provider'
                        billing_provider['name'] = entity_data['name']
                        billing_provider['taxId'] = entity_data['id']
                        billing_provider['address'] = {}
                    
                    elif entity_code == '87':  # Pay-To Provider
                        current_entity = 'pay_to_provider'
                        pay_to_provider['name'] = entity_data['name']
                        pay_to_provider['taxId'] = entity_data['id']
                        pay_to_provider['address'] = {}
                    
                    elif entity_code == 'IL':  # Subscriber
                        current_entity = 'subscriber'
                        subscriber['firstName'] = entity_data['firstName']
                        subscriber['lastName'] = entity_data['lastName']
                        subscriber['id'] = entity_data['id']
                        subscriber['address'] = {}
                    
                    elif entity_code == 'PR':  # Payer
                        current_entity = 'payer'
                        if current_claim:
                            current_claim['payer'] = {
                                'name': entity_data['name'],
                                'payerId': entity_data['id']
                            }
                        else:
                            payer['name'] = entity_data['name']
                            payer['payerId'] = entity_data['id']
                    
                    elif entity_code == '82':  # Rendering Provider
                        current_entity = 'rendering_provider'
                        if current_claim:
                            current_claim['renderingProvider'] = {
                                'firstName': entity_data['firstName'],
                                'lastName': entity_data['lastName'],
                                'npi': entity_data['id']
                            }
                    
                    elif entity_code == '77':  # Service Facility
                        current_entity = 'service_facility'
                        if current_claim:
                            current_claim['serviceFacility'] = {
                                'name': entity_data['name'],
                                'taxId': entity_data['id'],
                                'address': {}
                            }
                
                # N3 - Address
                elif seg_id == 'N3':
                    address_data = {
                        'street': clean_value(elements[1] if len(elements) > 1 else "")
                    }
                    temp_addresses[current_entity] = address_data
                
                # N4 - Geographic Location
                elif seg_id == 'N4':
                    if current_entity in temp_addresses:
                        temp_addresses[current_entity].update({
                            'city': clean_value(elements[1] if len(elements) > 1 else ""),
                            'state': clean_value(elements[2] if len(elements) > 2 else ""),
                            'zip': clean_value(elements[3] if len(elements) > 3 else "")
                        })
                        
                        if current_entity == 'billing_provider':
                            billing_provider['address'] = temp_addresses[current_entity]
                        elif current_entity == 'pay_to_provider':
                            pay_to_provider['address'] = temp_addresses[current_entity]
                        elif current_entity == 'subscriber':
                            subscriber['address'] = temp_addresses[current_entity]
                        elif current_entity == 'service_facility' and current_claim:
                            if 'serviceFacility' in current_claim:
                                current_claim['serviceFacility']['address'] = temp_addresses[current_entity]
                
                # PER - Contact Information
                elif seg_id == 'PER':
                    if current_entity == 'submitter':
                        submitter['contact'] = {
                            'name': clean_value(elements[2] if len(elements) > 2 else ""),
                            'phone': clean_value(elements[4] if len(elements) > 4 else ""),
                            'extension': clean_value(elements[6] if len(elements) > 6 else "")
                        }
                
                # SBR - Subscriber Information
                elif seg_id == 'SBR':
                    subscriber['relationship'] = clean_value(elements[2] if len(elements) > 2 else "self")
                    subscriber['groupNumber'] = clean_value(elements[3] if len(elements) > 3 else "")
                    subscriber['planType'] = clean_value(elements[5] if len(elements) > 5 else "")
                
                # DMG - Demographics
                elif seg_id == 'DMG':
                    if current_entity == 'subscriber':
                        subscriber['dob'] = parse_date(clean_value(elements[2] if len(elements) > 2 else ""))
                        subscriber['sex'] = clean_value(elements[3] if len(elements) > 3 else "")
                
                # CLM - Claim Information
                elif seg_id == 'CLM':
                    if current_claim:
                        claims_data.append(current_claim)
                    
                    current_claim = {
                        'id': clean_value(elements[1] if len(elements) > 1 else ""),
                        'totalCharge': safe_float(elements[2] if len(elements) > 2 else ""),
                        'placeOfService': "",
                        'serviceType': "",
                        'indicators': {
                            'assigned': clean_value(elements[7] if len(elements) > 7 else ""),
                            'providerSignature': clean_value(elements[6] if len(elements) > 6 else ""),
                            'releaseInfo': clean_value(elements[9] if len(elements) > 9 else ""),
                            'patientSignature': clean_value(elements[8] if len(elements) > 8 else ""),
                            'relatedCause': ""
                        },
                        'onsetDate': "",
                        'clearinghouseClaimNumber': "",
                        'diagnosis': {'primary': "", 'secondary': []},
                        'serviceLines': []
                    }
                
                # HI - Health Care Diagnosis Code
                elif seg_id == 'HI' and current_claim:
                    for i in range(1, len(elements)):
                        if elements[i]:
                            code = clean_code(elements[i])
                            if i == 1:
                                current_claim['diagnosis']['primary'] = code
                            else:
                                current_claim['diagnosis']['secondary'].append(code)
                
                # DTP - Date/Time/Period
                elif seg_id == 'DTP':
                    date_qualifier = clean_value(elements[1] if len(elements) > 1 else "")
                    date_value = parse_date(clean_value(elements[3] if len(elements) > 3 else ""))
                    
                    # 472 = Service date
                    if date_qualifier == '472' and current_claim and current_claim['serviceLines']:
                        if len(current_claim['serviceLines']) > 0:
                            current_claim['serviceLines'][-1]['serviceDate'] = date_value
                    
                    # 431/454 = Onset/Admission date
                    elif date_qualifier in ['431', '454'] and current_claim:
                        current_claim['onsetDate'] = date_value
                
                # REF - Reference Information
                elif seg_id == 'REF' and current_claim:
                    ref_qualifier = clean_value(elements[1] if len(elements) > 1 else "")
                    ref_value = clean_value(elements[2] if len(elements) > 2 else "")
                    
                    if ref_qualifier == 'D9':
                        current_claim['clearinghouseClaimNumber'] = ref_value
                
                # LX - Service Line Number
                elif seg_id == 'LX' and current_claim:
                    line_number = safe_int(elements[1] if len(elements) > 1 else "")
                    current_claim['serviceLines'].append({
                        'lineNumber': line_number,
                        'codeQualifier': "",
                        'procedureCode': "",
                        'charge': 0,
                        'unitQualifier': "",
                        'units': 0,
                        'diagnosisPointer': "",
                        'emergencyIndicator': "",
                        'serviceDate': ""
                    })
                
                # SV1 - Professional Service
                elif seg_id == 'SV1' and current_claim and current_claim['serviceLines']:
                    service_line = current_claim['serviceLines'][-1]
                    
                    procedure_info = clean_value(elements[1] if len(elements) > 1 else "")
                    if ':' in procedure_info:
                        parts = procedure_info.split(':')
                        service_line['codeQualifier'] = parts[0]
                        service_line['procedureCode'] = parts[1] if len(parts) > 1 else procedure_info
                    else:
                        service_line['procedureCode'] = procedure_info
                    
                    service_line['charge'] = safe_float(elements[2] if len(elements) > 2 else "")
                    service_line['unitQualifier'] = clean_value(elements[3] if len(elements) > 3 else "")
                    service_line['units'] = safe_float(elements[4] if len(elements) > 4 else "")
                    
                    if len(elements) > 5 and elements[5]:
                        service_line['placeOfService'] = clean_value(elements[5])
                        if not current_claim['placeOfService']:
                            current_claim['placeOfService'] = clean_value(elements[5])
                    
                    if len(elements) > 7 and elements[7]:
                        service_line['diagnosisPointer'] = safe_int(elements[7])
            
            if current_claim:
                claims_data.append(current_claim)
            
            if not pay_to_provider.get('name'):
                pay_to_provider = billing_provider.copy()
            
            # Build section arrays
            results = []
            
            for claim_data in claims_data:
                sections = [
                    {"section": "transaction", "data": transaction},
                    {"section": "submitter", "data": submitter},
                    {"section": "receiver", "data": receiver},
                    {"section": "billing_Provider", "data": billing_provider},
                    {"section": "Pay_To_provider", "data": pay_to_provider},
                    {"section": "subscriber", "data": subscriber},
                    {"section": "payer", "data": claim_data.get('payer', payer)},
                    {"section": "claim", "data": {
                        'id': claim_data['id'],
                        'totalCharge': claim_data['totalCharge'],
                        'placeOfService': claim_data['placeOfService'],
                        'serviceType': claim_data['serviceType'],
                        'indicators': claim_data['indicators'],
                        'onsetDate': claim_data['onsetDate'],
                        'clearinghouseClaimNumber': claim_data['clearinghouseClaimNumber']
                    }},
                    {"section": "diagnosis", "data": claim_data['diagnosis']},
                    {"section": "renderingProvider", "data": claim_data.get('renderingProvider', {})},
                    {"section": "serviceFacility", "data": claim_data.get('serviceFacility', billing_provider)},
                    {"section": "service_Lines", "data": claim_data['serviceLines']}
                ]
                
                results.append(sections)
            
            return results[0] if len(results) == 1 else results
    
    except Exception as e:
        raise RuntimeError(f"Error parsing X12 file: {str(e)}")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("X12 Parser for Claim Viewer")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 parser_for_viewer.py <input_file> [output_file]")
        print("=" * 70)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        os.makedirs("output_files_viewer", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"output_files_viewer/{base_name}_claim.json"
    
    print(f"\n🔄 Parsing X12 file for claim viewer...\n")
    print(f"📄 Input:  {input_file}")
    
    try:
        data = parse_x12_for_viewer(input_file)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Parsing complete!")
        print(f"💾 Output: {output_file}")
        
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict) and 'section' in data[0]:
                print(f"📊 Generated {len(data)} sections")
            else:
                print(f"📊 Multiple claims: {len(data)} claim arrays")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()