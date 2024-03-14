create_users_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "position": {"type": "string"},
                    "employer": {"type": "string"},
                    "area_of_clinical_ex": {"type": "string"},
                },
                "required": [
                    "email",
                ],
            },
        }
    },
    "required": ["users"],
}
