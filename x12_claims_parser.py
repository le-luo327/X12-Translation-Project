#!/usr/bin/env python3
"""
X12 837P Complete Structured Parser with All Information
Uses PyX12 to create organized JSON with business headers
Includes ALL data - no filtering
"""

import json
import sys
import os
from pyx12.x12file import X12Reader


def translate_x12_complete_structured(filepath):
    """
    Translate X12 to structured JSON with ALL information
    Returns complete hierarchical structure with business headers
    """
    result = {
        "file_info": {
            "source_file": filepath,
            "file_type": "X12 837P Professional Healthcare Claim"
        },
        "interchange_header": {},
        "functional_group": {},
        "transaction_set": {},
        "billing_provider": {},
        "subscriber": {},
        "claims": [],
        "all_segments": []  # Keep complete raw data too
    }
    
    current_claim = None
    current_service_lines = []
    
    try:
        with open(filepath, 'r') as f:
            reader = X12Reader(f)
            
            for segment in reader:
                seg_id = segment.get_seg_id()
                
                # Get complete segment data
                seg_str = str(segment)
                elements = seg_str.split('*')
                
                # Store in all_segments (complete raw data)
                result["all_segments"].append({
                    "segment_id": seg_id,
                    "elements": elements
                })
                
                # Parse into structured format
                
                # ISA - Interchange Control Header
                if seg_id == 'ISA':
                    result["interchange_header"] = {
                        "segment_id": "ISA",
                        "authorization_info_qualifier": elements[1] if len(elements) > 1 else "",
                        "authorization_info": elements[2] if len(elements) > 2 else "",
                        "security_info_qualifier": elements[3] if len(elements) > 3 else "",
                        "security_info": elements[4] if len(elements) > 4 else "",
                        "sender_id_qualifier": elements[5] if len(elements) > 5 else "",
                        "sender_id": elements[6] if len(elements) > 6 else "",
                        "receiver_id_qualifier": elements[7] if len(elements) > 7 else "",
                        "receiver_id": elements[8] if len(elements) > 8 else "",
                        "interchange_date": elements[9] if len(elements) > 9 else "",
                        "interchange_time": elements[10] if len(elements) > 10 else "",
                        "standards_id": elements[11] if len(elements) > 11 else "",
                        "version_number": elements[12] if len(elements) > 12 else "",
                        "interchange_control_number": elements[13] if len(elements) > 13 else "",
                        "acknowledgment_requested": elements[14] if len(elements) > 14 else "",
                        "usage_indicator": elements[15] if len(elements) > 15 else "",
                        "all_elements": elements
                    }
                
                # GS - Functional Group Header
                elif seg_id == 'GS':
                    result["functional_group"] = {
                        "segment_id": "GS",
                        "functional_id_code": elements[1] if len(elements) > 1 else "",
                        "application_sender_code": elements[2] if len(elements) > 2 else "",
                        "application_receiver_code": elements[3] if len(elements) > 3 else "",
                        "date": elements[4] if len(elements) > 4 else "",
                        "time": elements[5] if len(elements) > 5 else "",
                        "group_control_number": elements[6] if len(elements) > 6 else "",
                        "responsible_agency_code": elements[7] if len(elements) > 7 else "",
                        "version_code": elements[8] if len(elements) > 8 else "",
                        "all_elements": elements
                    }
                
                # ST - Transaction Set Header
                elif seg_id == 'ST':
                    result["transaction_set"] = {
                        "segment_id": "ST",
                        "transaction_set_id": elements[1] if len(elements) > 1 else "",
                        "transaction_control_number": elements[2] if len(elements) > 2 else "",
                        "implementation_convention_ref": elements[3] if len(elements) > 3 else "",
                        "all_elements": elements
                    }
                
                # BHT - Beginning of Hierarchical Transaction
                elif seg_id == 'BHT':
                    result["transaction_set"]["beginning_hierarchical_transaction"] = {
                        "segment_id": "BHT",
                        "hierarchical_structure_code": elements[1] if len(elements) > 1 else "",
                        "transaction_set_purpose_code": elements[2] if len(elements) > 2 else "",
                        "reference_id": elements[3] if len(elements) > 3 else "",
                        "date": elements[4] if len(elements) > 4 else "",
                        "time": elements[5] if len(elements) > 5 else "",
                        "claim_type": elements[6] if len(elements) > 6 else "",
                        "all_elements": elements
                    }
                
                # NM1 - Name/Entity
                elif seg_id == 'NM1':
                    entity_code = elements[1] if len(elements) > 1 else ""
                    entity_data = {
                        "segment_id": "NM1",
                        "entity_id_code": entity_code,
                        "entity_type_qualifier": elements[2] if len(elements) > 2 else "",
                        "name_last_or_organization": elements[3] if len(elements) > 3 else "",
                        "name_first": elements[4] if len(elements) > 4 else "",
                        "name_middle": elements[5] if len(elements) > 5 else "",
                        "name_prefix": elements[6] if len(elements) > 6 else "",
                        "name_suffix": elements[7] if len(elements) > 7 else "",
                        "id_code_qualifier": elements[8] if len(elements) > 8 else "",
                        "id_code": elements[9] if len(elements) > 9 else "",
                        "all_elements": elements
                    }
                    
                    # Categorize by entity type
                    if entity_code == '85':  # Billing Provider
                        result["billing_provider"] = entity_data
                    elif entity_code == 'IL':  # Subscriber
                        result["subscriber"] = entity_data
                    elif entity_code == 'QC':  # Patient
                        if current_claim:
                            current_claim["patient"] = entity_data
                    elif entity_code == 'PR':  # Payer
                        if current_claim:
                            current_claim["payer"] = entity_data
                    elif entity_code == '82':  # Rendering Provider
                        if current_claim:
                            current_claim["rendering_provider"] = entity_data
                    else:
                        # Store other entities
                        if "other_entities" not in result:
                            result["other_entities"] = []
                        result["other_entities"].append(entity_data)
                
                # N3 - Address
                elif seg_id == 'N3':
                    address_data = {
                        "segment_id": "N3",
                        "address_line_1": elements[1] if len(elements) > 1 else "",
                        "address_line_2": elements[2] if len(elements) > 2 else "",
                        "all_elements": elements
                    }
                    # Add to most recent entity
                    if current_claim and "patient" in current_claim:
                        current_claim["patient"]["address"] = address_data
                    elif result["billing_provider"]:
                        result["billing_provider"]["address"] = address_data
                
                # N4 - Geographic Location
                elif seg_id == 'N4':
                    location_data = {
                        "segment_id": "N4",
                        "city": elements[1] if len(elements) > 1 else "",
                        "state": elements[2] if len(elements) > 2 else "",
                        "postal_code": elements[3] if len(elements) > 3 else "",
                        "country_code": elements[4] if len(elements) > 4 else "",
                        "all_elements": elements
                    }
                    if current_claim and "patient" in current_claim:
                        current_claim["patient"]["geographic_location"] = location_data
                    elif result["billing_provider"]:
                        result["billing_provider"]["geographic_location"] = location_data
                
                # REF - Reference Information
                elif seg_id == 'REF':
                    ref_data = {
                        "segment_id": "REF",
                        "reference_id_qualifier": elements[1] if len(elements) > 1 else "",
                        "reference_id": elements[2] if len(elements) > 2 else "",
                        "description": elements[3] if len(elements) > 3 else "",
                        "all_elements": elements
                    }
                    if current_claim:
                        if "references" not in current_claim:
                            current_claim["references"] = []
                        current_claim["references"].append(ref_data)
                    else:
                        if "header_references" not in result:
                            result["header_references"] = []
                        result["header_references"].append(ref_data)
                
                # PER - Contact Information
                elif seg_id == 'PER':
                    contact_data = {
                        "segment_id": "PER",
                        "contact_function_code": elements[1] if len(elements) > 1 else "",
                        "name": elements[2] if len(elements) > 2 else "",
                        "communication_number_qualifier_1": elements[3] if len(elements) > 3 else "",
                        "communication_number_1": elements[4] if len(elements) > 4 else "",
                        "communication_number_qualifier_2": elements[5] if len(elements) > 5 else "",
                        "communication_number_2": elements[6] if len(elements) > 6 else "",
                        "all_elements": elements
                    }
                    if "contacts" not in result:
                        result["contacts"] = []
                    result["contacts"].append(contact_data)
                
                # CLM - Claim Information (start new claim)
                elif seg_id == 'CLM':
                    # Save previous claim
                    if current_claim:
                        current_claim["service_lines"] = current_service_lines
                        result["claims"].append(current_claim)
                    
                    # Start new claim
                    current_claim = {
                        "segment_id": "CLM",
                        "claim_id": elements[1] if len(elements) > 1 else "",
                        "total_charge": elements[2] if len(elements) > 2 else "",
                        "claim_filing_indicator": elements[5] if len(elements) > 5 else "",
                        "provider_signature_indicator": elements[6] if len(elements) > 6 else "",
                        "assignment_plan": elements[7] if len(elements) > 7 else "",
                        "benefits_assignment": elements[8] if len(elements) > 8 else "",
                        "release_info": elements[9] if len(elements) > 9 else "",
                        "all_elements": elements
                    }
                    current_service_lines = []
                
                # HI - Health Care Diagnosis Code
                elif seg_id == 'HI' and current_claim:
                    diagnosis_codes = []
                    for i in range(1, len(elements)):
                        if elements[i]:
                            diagnosis_codes.append(elements[i])
                    current_claim["diagnosis_codes"] = {
                        "segment_id": "HI",
                        "codes": diagnosis_codes,
                        "all_elements": elements
                    }
                
                # DTP - Date/Time/Period
                elif seg_id == 'DTP':
                    date_data = {
                        "segment_id": "DTP",
                        "date_qualifier": elements[1] if len(elements) > 1 else "",
                        "date_format": elements[2] if len(elements) > 2 else "",
                        "date_value": elements[3] if len(elements) > 3 else "",
                        "all_elements": elements
                    }
                    if current_claim:
                        if "dates" not in current_claim:
                            current_claim["dates"] = []
                        current_claim["dates"].append(date_data)
                
                # LX - Service Line Number
                elif seg_id == 'LX' and current_claim:
                    current_service_line = {
                        "segment_id": "LX",
                        "line_number": elements[1] if len(elements) > 1 else "",
                        "all_elements": elements
                    }
                    current_service_lines.append(current_service_line)
                
                # SV1 - Professional Service
                elif seg_id == 'SV1' and current_claim and current_service_lines:
                    current_service_lines[-1]["service_info"] = {
                        "segment_id": "SV1",
                        "procedure_info": elements[1] if len(elements) > 1 else "",
                        "line_charge": elements[2] if len(elements) > 2 else "",
                        "unit_basis": elements[3] if len(elements) > 3 else "",
                        "unit_count": elements[4] if len(elements) > 4 else "",
                        "place_of_service": elements[5] if len(elements) > 5 else "",
                        "diagnosis_pointer": elements[7] if len(elements) > 7 else "",
                        "all_elements": elements
                    }
                
                # HL - Hierarchical Level
                elif seg_id == 'HL':
                    hl_data = {
                        "segment_id": "HL",
                        "hierarchical_id": elements[1] if len(elements) > 1 else "",
                        "parent_id": elements[2] if len(elements) > 2 else "",
                        "level_code": elements[3] if len(elements) > 3 else "",
                        "child_code": elements[4] if len(elements) > 4 else "",
                        "all_elements": elements
                    }
                    if "hierarchical_levels" not in result:
                        result["hierarchical_levels"] = []
                    result["hierarchical_levels"].append(hl_data)
                
                # SBR - Subscriber Information
                elif seg_id == 'SBR':
                    sbr_data = {
                        "segment_id": "SBR",
                        "payer_responsibility": elements[1] if len(elements) > 1 else "",
                        "individual_relationship": elements[2] if len(elements) > 2 else "",
                        "group_number": elements[3] if len(elements) > 3 else "",
                        "group_name": elements[4] if len(elements) > 4 else "",
                        "insurance_type": elements[5] if len(elements) > 5 else "",
                        "claim_filing_indicator": elements[9] if len(elements) > 9 else "",
                        "all_elements": elements
                    }
                    result["subscriber"]["insurance_info"] = sbr_data
                
                # PRV - Provider Information
                elif seg_id == 'PRV':
                    prv_data = {
                        "segment_id": "PRV",
                        "provider_code": elements[1] if len(elements) > 1 else "",
                        "reference_id_qualifier": elements[2] if len(elements) > 2 else "",
                        "reference_id": elements[3] if len(elements) > 3 else "",
                        "all_elements": elements
                    }
                    if "provider_info" not in result:
                        result["provider_info"] = []
                    result["provider_info"].append(prv_data)
                
                # DMG - Demographics
                elif seg_id == 'DMG':
                    dmg_data = {
                        "segment_id": "DMG",
                        "date_format": elements[1] if len(elements) > 1 else "",
                        "date_of_birth": elements[2] if len(elements) > 2 else "",
                        "gender": elements[3] if len(elements) > 3 else "",
                        "all_elements": elements
                    }
                    if current_claim and "patient" in current_claim:
                        current_claim["patient"]["demographics"] = dmg_data
                
                # AMT - Monetary Amount
                elif seg_id == 'AMT':
                    amt_data = {
                        "segment_id": "AMT",
                        "amount_qualifier": elements[1] if len(elements) > 1 else "",
                        "amount": elements[2] if len(elements) > 2 else "",
                        "all_elements": elements
                    }
                    if current_claim:
                        if "amounts" not in current_claim:
                            current_claim["amounts"] = []
                        current_claim["amounts"].append(amt_data)
            
            # Save last claim
            if current_claim:
                current_claim["service_lines"] = current_service_lines
                result["claims"].append(current_claim)
            
            # Add summary
            result["summary"] = {
                "total_segments": len(result["all_segments"]),
                "total_claims": len(result["claims"]),
                "total_service_lines": sum(len(claim.get("service_lines", [])) for claim in result["claims"])
            }
            
            return result
    
    except Exception as e:
        raise RuntimeError(f"Error translating X12 file: {str(e)}")


def validate_output(data):
    """Validate the structured output"""
    try:
        if not isinstance(data, dict):
            return False, "Output must be a dictionary"
        
        if "all_segments" not in data or len(data["all_segments"]) == 0:
            return False, "No segments found"
        
        if "summary" not in data:
            return False, "Missing summary"
        
        return True, "Valid"
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def save_with_validation(data, output_file):
    """Save with validation"""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Translation complete!")
    print(f"💾 Output: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Total segments: {data['summary']['total_segments']}")
    print(f"   - Total claims: {data['summary']['total_claims']}")
    print(f"   - Total service lines: {data['summary']['total_service_lines']}")
    
    print(f"\n🔍 Validating JSON output...")
    
    # JSON syntax
    try:
        with open(output_file, 'r') as f:
            json.load(f)
        print(f"   ✅ JSON syntax valid")
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON syntax error: {e}")
        return False
    
    # Structure validation
    is_valid, msg = validate_output(data)
    if is_valid:
        print(f"   ✅ Structure validation passed")
    else:
        print(f"   ❌ Structure validation failed: {msg}")
        return False
    
    print(f"\n✅ All validations passed!")
    return True


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("X12 837P Complete Structured Parser")
        print("=" * 70)
        print("\nFeatures:")
        print("  ✅ Structured output with business headers")
        print("  ✅ ALL information included (no filtering)")
        print("  ✅ Automatic validation")
        print("\nUsage:")
        print("  python3 x12_claims_parser.py <input_file> [output_file]")
        print("\nExamples:")
        print("  python3 x12_claims_parser.py input_files/X12-837.txt")
        print("=" * 70)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        os.makedirs("output_files", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"output_files/{base_name}_parsed.json"
    
    print(f"\n🔄 Translating X12 file to structured JSON...\n")
    print(f"📄 Input:  {input_file}")
    
    try:
        data = translate_x12_complete_structured(input_file)
        success = save_with_validation(data, output_file)
        
        if success:
            print(f"\n💡 To view output:")
            print(f"   python3 -m json.tool {output_file} | less")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()