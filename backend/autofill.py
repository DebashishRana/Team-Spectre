def autofill(form_fields, user_data):
    filled = {}

    for field in form_fields:
        mapped_key = map_field(field)

        if mapped_key != "unknown":
            filled[field] = user_data.get(mapped_key)
        else:
            filled[field] = None

    return filled

def map_field(field_name):
    field_name = field_name.lower()

    for key in FIELD_MAPPING:
        if key in field_name:
            return FIELD_MAPPING[key]

    return "unknown"