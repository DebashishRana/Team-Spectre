import re
import pytesseract
from PIL import Image

def extract_aadhaar_details(image_path: str):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return {'error': str(e)}

    # 1. Validate Aadhaar Number
    aadhaar_pattern = re.compile(r'^[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}$', re.MULTILINE)
    aadhaar_match = aadhaar_pattern.search(text)
    if not aadhaar_match:
        return 'no aadhar detected'

    details = {'document_type': 'Aadhaar'}

    # 2. Extract Details (Basic heuristics)
    # Name usually comes after 'DOB' or 'Year of Birth'
    # DOB
    dob_match = re.search(r'(DOB|Year of Birth|YOB)\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4}|\d{4})', text, re.IGNORECASE)
    if dob_match:
        details['dob'] = dob_match.group(2)

    # Address usually comes after 'Address'
    address_match = re.search(r'Address\s*[:\-]?\s*(.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if address_match:
        details['address'] = address_match.group(1).replace('\n', ' ').strip()

    # Marital Status (Not standard on Aadhaar, but searching for W/O, S/O, D/O can imply relations)
    # Marital status keyword (if any custom formats exist)
    marital_match = re.search(r'(Married|Unmarried|Single)', text, re.IGNORECASE)
    if marital_match:
        details['marital_status'] = marital_match.group(1).title()
    else:
        # Implied marital status for women via W/O (Wife of)
        if re.search(r'W/O', text, re.IGNORECASE):
            details['marital_status'] = 'Married'
        else:
            details['marital_status'] = 'Unknown/Not Found'

    # Name heuristic (Looking for typical Indian name patterns, usually all caps, next to DOB)
    # For real use, NLP or fixed bounding box coordinates works best.
    name_match = re.search(r'([A-Z][a-z]+(\s[A-Z][a-z]+)*)', text)
    if name_match:
        details['name'] = name_match.group(1)

    return details

