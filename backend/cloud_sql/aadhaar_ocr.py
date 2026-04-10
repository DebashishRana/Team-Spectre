import re
import pytesseract
from PIL import Image

def extract_aadhaar_details(image_path: str):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return {'error': str(e)}

    # 1. Validate Aadhaar Number precisely as requested
    aadhaar_pattern = re.compile(r'^[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}$', re.MULTILINE)
    aadhaar_match = aadhaar_pattern.search(text)
    if not aadhaar_match:
        return 'no aadhar detected'

    details = {'document_type': 'Aadhaar'}

    # 2. Extract Name (Typically capitalized and near the top, basic heuristic)
    name_match = re.search(r'^([A-Z][A-Za-z]+(\s[A-Z][A-Za-z]+)+)$', text, re.MULTILINE)
    details['name'] = name_match.group(1).strip() if name_match else 'Not Found'

    # 3. Extract DOB
    dob_match = re.search(r'(DOB|Year of Birth|YOB)\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4}|\d{4})', text, re.IGNORECASE)
    details['dob'] = dob_match.group(2) if dob_match else 'Not Found'

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

