import re
import easyocr
from PIL import Image

# Initialize EasyOCR reader (lazy load on first use)
_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def extract_aadhaar_details(image_path: str):
    try:
        reader = _get_reader()
        result = reader.readtext(image_path)
        
        # EasyOCR returns list of (bbox, text, confidence)
        # Extract all text lines
        text_lines = [line[1] for line in result]
        text = '\n'.join(text_lines)
    except Exception as e:
        return {'error': str(e)}

    # 1. Extract Aadhaar Number precisely as requested
    aadhaar_pattern = re.compile(r'^[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}$', re.MULTILINE)
    aadhaar_match = aadhaar_pattern.search(text)
    if not aadhaar_match:
        return 'no aadhar detected'

    details = {'document_type': 'Aadhaar'}
    aadhaar_num = aadhaar_match.group(0).strip()
    details['aadhaar_numbers'] = [aadhaar_num]

    # 2. Extract Name (Typically capitalized and near the top, basic heuristic)
    name_match = re.search(r'^([A-Z][A-Za-z]+(\s[A-Z][A-Za-z]+)+)$', text, re.MULTILINE)
    holder_name = name_match.group(1).strip() if name_match else 'Not Found'
    details['holder_name'] = holder_name
    details['name'] = holder_name  # For backward compatibility

    # 3. Extract DOB
    dob_match = re.search(r'(DOB|Year of Birth|YOB)\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4}|\d{4})', text, re.IGNORECASE)
    dob = dob_match.group(2) if dob_match else 'Not Found'
    details['date_of_birth'] = dob
    details['dob'] = dob  # For backward compatibility

    # 4. Extract Address
    address_match = re.search(r'Address\s*[:\-]?\s*(.*?)(?=\n([A-Z]|\Z))', text, re.IGNORECASE | re.DOTALL)
    if address_match:
        details['address'] = address_match.group(1).replace('\n', ' ').strip()
    else:
        details['address'] = 'Not Found'

    # 5. Extract Marital Status (Using relation heuristics like W/O wife of)
    if re.search(r'\bW/O\b', text, re.IGNORECASE):
        details['marital_status'] = 'Married'
    else:
        marital_match = re.search(r'(Married|Unmarried|Single)', text, re.IGNORECASE)
        details['marital_status'] = marital_match.group(1).title() if marital_match else 'Unknown (Not explicitly stated on standard Aadhaar)'

    return details

