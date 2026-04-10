"""Auto-fill module for form field mapping and reuse"""

# Field mapping: Form field names → Universal schema fields
FIELD_MAPPING = {
    # Name fields
    "name": "full_name",
    "applicant name": "full_name",
    "full name": "full_name",
    "applicant_name": "full_name",
    "applicant-name": "full_name",

    # DOB fields
    "dob": "date_of_birth",
    "date of birth": "date_of_birth",
    "birth date": "date_of_birth",
    "date_of_birth": "date_of_birth",
    "date-of-birth": "date_of_birth",

    # Gender
    "gender": "gender",
    "sex": "gender",

    # ID/Aadhaar/PAN
    "aadhaar": "id_number",
    "aadhaar number": "id_number",
    "aadhar": "id_number",
    "id number": "id_number",
    "id_number": "id_number",
    "pan": "id_number",
    "pan number": "id_number",

    # Phone
    "mobile": "phone",
    "phone": "phone",
    "mobile number": "phone",
    "phone number": "phone",
    "mobile_number": "phone",
    "phone_number": "phone",

    # Address
    "address": "address",
    "residential address": "address",
    "current address": "address",
}


def autofill(form_fields, user_data):
    """
    Auto-fill form fields using user's stored data.
    
    Args:
        form_fields: List of form field names to fill
        user_data: Dict of user data (from decrypted document)
    
    Returns:
        Dict with form_fields as keys and user_data values
    """
    filled = {}

    for field in form_fields:
        mapped_key = map_field(field)

        if mapped_key != "unknown":
            filled[field] = user_data.get(mapped_key)
        else:
            filled[field] = None

    return filled


def map_field(field_name: str) -> str:
    """
    Map form field name to universal schema field.
    
    Args:
        field_name: Name of form field
    
    Returns:
        Mapped field name or "unknown" if no match
    """
    field_name_lower = field_name.lower().strip()

    # Exact match first
    if field_name_lower in FIELD_MAPPING:
        return FIELD_MAPPING[field_name_lower]

    # Substring match
    for key in FIELD_MAPPING:
        if key in field_name_lower:
            return FIELD_MAPPING[key]

    return "unknown"