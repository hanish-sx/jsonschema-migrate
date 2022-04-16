import re
from datetime import datetime

from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError



PLACE_HOLDER = 'No data found'
NULLS = ['No information', 'no data found', None, 'null', 'None', '']

# Schema used for the date format
# It only checks for the 
SCHEMA_DATE_STR = {
    "type": ["string", "null"],
}
format_checker = FormatChecker()
@format_checker.checks('normal_date')
def normal_date(value):
    if value == None:
        return True
    if value == 'None':
        return True
    if value == PLACE_HOLDER:
        return True
    try:
        datetime.strptime(value, '%m/%d/%Y')
    except Exception:
        return False
    return True

# Schema used for the date format of DOB
# It is strictly string and must contain a date
SCHEMA_DOB_STR = {
    "type": "string",
}
format_checker = FormatChecker()
@format_checker.checks('normal_dob')
def normal_dob(value):
    try:
        datetime.strptime(value, '%m/%d/%Y')
    except Exception:
        return False
    return True

# A set of strings that are allowed in phone numbers
# This will be used to verify the format of phone values
ACCEPTED_PHONE_STRS = {
    '-', '(', ')', '+',
}
@format_checker.checks('normal_phone_number')
def normal_phone_number(value):
    if value is None:
        return False
    if value == PLACE_HOLDER:
        return True
    value = value.strip()
    if len(value) < 5:
        return False
    if value.startswith('-'):
        return False
    if value.endswith('-'):
        return False
    if value == '(000)000-0000':
        return False
    non_number = set(x.strip() for x in re.findall(r'\D', value) if x.strip())
    non_number = set(x for x in non_number if x not in ACCEPTED_PHONE_STRS)
    if len(non_number) != 0:
        return False
    return True

# The file name should not be a placeholder or null type value
SCHEMA_FILE_NAME = {
    "type": "string",
}
@format_checker.checks('normal_file_name')
def normal_file_name(value):
    if value in NULLS:
        return False
    if isinstance(value, str):
        if value.strip() in NULLS:
            return False
    return True

# Age must be a string with an integer value
@format_checker.checks('normal_age')
def normal_age(value):
    if value in NULLS:
        return False
    if not isinstance(value, str):
        return False
    try:
        if int(value) not in range(1,151):
            return False
    except ValueError:
        # Non numeric value
        return False
    return True

# Format to check that a value is not an empty string
@format_checker.checks('non_empty_string')
def non_empty_string(value):
    if not value or value in NULLS:
        return False
    return True

# Format to check that a name is reasonable or not
@format_checker.checks('normal_name')
def normal_name(value):
    if not non_empty_string(value):
        return False
    if not value.count(" ") < 6:
        return False
    return bool(re.match(r'^[ a-zA-Z\.\-\,\']{1,150}$', value))

encounter_schema = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "properties": {
        "encdate": SCHEMA_DATE_STR,
        "ehr_id": {
            "type": "string",
            "format": "non_empty_string",
        },
        "demographics": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "object",
                            "properties": {
                                "prefix": {
                                    "type": "null"
                                },
                                "given": {
                                    "type": "string",
                                },
                                "family": {
                                    "type": "string",
                                }
                            },
                            "required": [
                                "family",
                                "given"
                            ]
                        },
                        "dob": SCHEMA_DOB_STR,
                        "gender": {
                            "type": [
                                "null",
                                "string"
                            ],
                        },
                        "marital_status": {
                            "type": ["string", "null"]
                        },
                        "address": {
                            "type": "object",
                            "properties": {
                                "street": {
                                    "type": "string"
                                },
                                "city": {
                                    "type": "string"
                                },
                                "state": {
                                    "type": "string"
                                },
                                "zip": {
                                    "type": "string"
                                },
                                "country": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "city",
                                "country",
                                "state",
                                "street",
                                "zip"
                            ]
                        },
                        "phone": {
                            "type": "object",
                            # Only using "additionalProperties" allows putting this
                            # type/format constraint on all keys inside this object.
                            "additionalProperties": {
                                "type": "string",
                            },
                            # "required": [
                            #     "home",
                            #     "mobile",
                            #     "work"
                            # ]
                        },
                        "email": {
                            "type": "string"
                        },
                        "language": {
                            "type": "string"
                        },
                        "guardian": {
                            "anyOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "object",
                                            "properties": {
                                                "given": {
                                                    "type": ["string", "array"],
                                                    "items": {
                                                        "type": "string"
                                                    }
                                                },
                                                "family": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                }
                                            },
                                            "required": [
                                                "family",
                                                "given"
                                            ]
                                        },
                                        "relationship": {
                                            "type": [
                                                "null",
                                                "string"
                                            ]
                                        },
                                        "address": {
                                            "type": "object",
                                            "properties": {
                                                "street": {
                                                    "type": ["string", "array"]
                                                },
                                                "city": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                },
                                                "state": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                },
                                                "zip": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                },
                                                "country": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                }
                                            },
                                            "required": [
                                                "city",
                                                "country",
                                                "state",
                                                "street",
                                                "zip"
                                            ]
                                        },
                                        "phone": {
                                            "type": "object",
                                            "properties": {
                                                "home": {
                                                    "type": [
                                                        "null",
                                                        "string"
                                                    ]
                                                }
                                            },
                                            # "required": [
                                            #     "home"
                                            # ]
                                        },
                                        "relationship_code": {
                                            "type": "null"
                                        }
                                    },
                                    # "required": [
                                    #     "address",
                                    #     "name",
                                    #     "phone",
                                    #     "relationship"
                                    # ]
                                },
                                {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "object",
                                                "properties": {
                                                    "given": {
                                                        "type": "string"
                                                    },
                                                    "family": {
                                                        "type": "null"
                                                    }
                                                },
                                                "required": [
                                                    "family",
                                                    "given"
                                                ]
                                            },
                                            "address": {
                                                "type": "object",
                                                "properties": {
                                                    "street": {
                                                        "type": "string"
                                                    },
                                                    "city": {
                                                        "type": "null"
                                                    },
                                                    "state": {
                                                        "type": "null"
                                                    },
                                                    "zip": {
                                                        "type": "null"
                                                    }
                                                },
                                                "required": [
                                                    "city",
                                                    "state",
                                                    "street",
                                                    "zip"
                                                ]
                                            },
                                            "phone": {
                                                "type": "object"
                                            },
                                            "relation": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "address",
                                            "name",
                                            "phone",
                                            "relation"
                                        ]
                                    }
                                }
                            ]
                        },
                        "provider": {
                            "type": "string",
                        },
                        "age": {
                            "type": "string",
                        },
                        "sex": {
                            "type": "string"
                        },
                        "patient_id": {
                            "type": "string",
                        },
                        "race": {
                            "type": "string"
                        },
                        "etnicity": {
                            "type": "string"
                        },
                        "sexual_orientation": {
                            "type": "string"
                        },
                        "gender_identity": {
                            "type": "string"
                        },
                        "previous_first_name": {
                            "type": "string"
                        },
                        "previous_last_name": {
                            "type": "string"
                        },
                        "file_name": SCHEMA_FILE_NAME,
                        "ethicity": {
                            "type": "string"
                        },
                        "account": {
                            "type": "string"
                        },
                        "ssn": {
                            "type": "string"
                        },
                        "email_list": {
                            "type": "object",
                            "properties": {
                                "PRIMARY": {
                                    "type": "string"
                                },
                                "email_2": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "PRIMARY"
                            ]
                        },
                        "ethnicity": {
                            "type": ["string", "null"]
                        },
                        "religion": {
                            "type": ["string", "null"]
                        },
                        "birthplace": {
                            "type": "object",
                            "properties": {
                                "state": {
                                    "type": "null"
                                },
                                "zip": {
                                    "type": "null"
                                },
                                "country": {
                                    "type": "null"
                                }
                            },
                            "required": [
                                "country",
                                "state",
                                "zip"
                            ]
                        },
                        "LastApptDate": {
                            "type": "string"
                        },
                        "NextApptDate": {
                            "type": "string"
                        },
                        "ethinicity": {
                            "type": "string"
                        },
                        "characterestic": {
                            "type": "string"
                        },
                        "birthorder": {
                            "type": "string"
                        },
                        "gestationalAge": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "address",
                        "age",
                        "dob",
                        "email",
                        "file_name",
                        "gender",
                        "guardian",
                        "language",
                        "marital_status",
                        "name",
                        "patient_id",
                        "phone",
                        "provider",
                        "sex"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "document": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "date": SCHEMA_DATE_STR,
                        "title": {
                            "type": "string"
                        },
                        "clinic": {
                            "type": "string"
                        },
                        "documentation_of": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "object",
                                        "properties": {
                                            "prefix": {
                                                "type": [
                                                    "null",
                                                    "string"
                                                ]
                                            },
                                            "given": {
                                                "type": ["string", "null"],
                                            },
                                            "family": {
                                                "type": ["string", "null"],
                                            }
                                        },
                                        "required": [
                                            "family",
                                            "given",
                                            "prefix"
                                        ]
                                    },
                                    "phone": {
                                        "type": "object",
                                        "properties": {
                                            "work": {
                                                "type": "string"
                                            },
                                            "work2": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "work"
                                        ]
                                    },
                                    "address": {
                                        "type": "object",
                                        "properties": {
                                            "street": {
                                                "anyOf": [
                                                    {
                                                        "type": "string"
                                                    },
                                                    {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string"
                                                        }
                                                    }
                                                ]
                                            },
                                            "city": {
                                                "type": "string"
                                            },
                                            "state": {
                                                "type": "string"
                                            },
                                            "zip": {
                                                "type": "string"
                                            },
                                            "country": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "city",
                                            "country",
                                            "state",
                                            "street",
                                            "zip"
                                        ]
                                    }
                                },
                                "required": [
                                    "address",
                                    "name",
                                    "phone"
                                ]
                            },
                            "default": [
                                {
                                    "name": {
                                        "prefix": None,
                                        "given": "[Dr_FIRSTNAME]",
                                        "family": "[Dr_LASTNAME]",
                                        "phone": "[PHONE]",
                                        "address": "[ADDRESS]"
                                    },
                                    "phone": {
                                        "work": "no data found"
                                    },
                                    "address": {
                                        "street": "no data found",
                                        "city": "no data found",
                                        "state": "no data found",
                                        "zip": "no data found",
                                        "country": ""
                                    }
                                }
                            ]
                        }
                    },
                    "required": [
                        "clinic",
                        "date",
                        "documentation_of"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "history_present_illness": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "medications": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": ["string", "null"]
                            },
                            "date": SCHEMA_DATE_STR,
                            "instructions": {
                                "type": ["string", "null"]
                            },
                            "medication": {
                                "type": "string"
                            },
                            "refill": {
                                "type": "string"
                            },
                            "quantity": {
                                "type": "string"
                            },
                            "start_date": {
                                "type": "string",
                            },
                            "end_date": {
                                "type": ["string", "null"],
                            },
                            "date_created": SCHEMA_DATE_STR,
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "medication",
                            "instructions",
                            "status",
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "review_of_systems": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "description": {
                                "type": "string"
                            },
                            "date": SCHEMA_DATE_STR
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "vitals": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "vitals": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "date",
                            "vitals"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "examination": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string"
                            },
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "date",
                            "description",
                            "type"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "assessments": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "code": {
                                "type": ["string", "null"]
                            },
                            "assessment": {
                                "type": "string"
                            },
                            "problem": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "code",
                            "assessment",
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "plan_of_treatment": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "problem": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "care_plan": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "date": SCHEMA_DATE_STR,
                            "unit": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "code": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "diagnosis": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "status": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "care_plan",
                            "date"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "patient_note": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "type": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "enc_type": {
            "type": "string",
            "format": "non_empty_string",
        },
        "doc_hash": {
            "type": "string"
        },
        "physician_npi": {
            "type": "string"
        },
        "job_id": {
            "type": "string"
        },
        "doc_id": {
            "type": ["string","null"]
        },
        "force": {
            "type": "boolean"
        },
        "created_at": {
            "type": "integer"
        },
        "allergies": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "allergen": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "reaction_type": {
                                "type": "string"
                            },
                            "description": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "substance": {
                                "type": "null"
                            }
                        },
                        "required": [
                            "allergen",
                            # "date"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "past_history": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "history": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "history"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "social_history": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "cheif_complaint": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "surgical_history": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "family_history": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "relation": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "description": {
                                "type": "string"
                            },
                            "date": SCHEMA_DATE_STR
                        },
                        "required": [
                            "description",
                            "relation"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "diagnoses": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "acuity": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "acuity",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "reason_for_visit": {
            "type": "object",
            "properties": {
                "parser": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": SCHEMA_DATE_STR,
                                    "description": {
                                        "type": [
                                            "null",
                                            "string"
                                        ]
                                    }
                                },
                                "required": [
                                    "date",
                                    "description"
                                ]
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "description"
                            ]
                        }
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "chief_complaint": {
            "type": "object",
            "properties": {
                "parser": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": SCHEMA_DATE_STR,
                                    "description": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "date",
                                    "description"
                                ]
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "description"
                            ]
                        }
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "procedures": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "prescription": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "encounters": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array"
                }
            },
            "required": [
                "parser"
            ]
        },
        "problems": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "problem": {
                                "type": "string"
                            },
                            "code": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            },
                            "status": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "functional_statuses": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array"
                }
            },
            "required": [
                "parser"
            ]
        },
        "immunizations": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "product": {
                                "type": "string"
                            },
                            "dose_quantity": {
                                "type": "null"
                            },
                            "instructions": {
                                "type": "null"
                            }
                        },
                        "required": [
                            "date",
                            # "dose_quantity",
                            # "instructions",
                            # "product"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "immunization_declines": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array"
                }
            },
            "required": [
                "parser"
            ]
        },
        "instructions": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array"
                }
            },
            "required": [
                "parser"
            ]
        },
        "results": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "name": {
                                "type": "string"
                            },
                            "value": {
                                "type": [
                                    "integer",
                                    "string"
                                ]
                            },
                            "unit": {
                                "type": ["string", "null"]
                            },
                            "code": {
                                "type": "string"
                            }
                        },
                        "required": [
                            # "code",
                            "date",
                            # "name",
                            # "unit",
                            # "value"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        },
        "mental_status": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array"
                }
            },
            "required": [
                "parser"
            ]
        },
        "goals": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "health_concerns": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "medical_equipment": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "reason_for_referral": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    # "default": {
                    #     "description": "No Information"
                    # },
                    "required": [
                        "description"
                    ]
                }
            },
            "default": {
                "parser": {
                    "description": "No Information"
                },
                "text_extract": {
                    "sections": [
                        "reason_for_referral"
                    ],
                    "tables": [],
                    "tables_xml": [],
                    "raw_text": "No Information"
                }
            },
            "required": [
                "parser"
            ]
        },
        "interventions": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "encounter_diagnosis": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "evaluations_outcomes": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "description"
                    ]
                }
            },
            "required": [
                "parser"
            ]
        },
        "hospitalization": {
            "type": "object",
            "properties": {
                "parser": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": SCHEMA_DATE_STR,
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "date",
                            "description"
                        ]
                    }
                }
            },
            "required": [
                "parser"
            ]
        }
    },
    "required": [
        "demographics",
        "document",
        "ehr_id",
        "enc_type",
        "encdate",
    ]
}

def validate_enc(enc):
    '''Validate a python data structure against the
    enocounter schema.

    A NoneType return means the encounter is valid.
    
    A string return means there is and error and the
    string contains the error mesage.
    '''
    try:
        validate(enc, schema=encounter_schema, format_checker=format_checker)
    except ValidationError as e:
        msg = e.message
        if e.absolute_path:
            path = ' -> '.join([str(x) for x in e.absolute_path])
        else:
            path = 'root'
        err_text = f"{msg} in {path}"
        return err_text

if __name__ == "__main__":

    import json
    import os
    import sys
    import logging

    path = sys.argv[1]

    error_logger = logging.getLogger('error')
    error_handler = logging.FileHandler('error.log')
    error_logger.addHandler(error_handler)

    key_error_logger = logging.getLogger('key_error')
    key_error_handler = logging.FileHandler('key_error.log')
    key_error_logger.addHandler(key_error_handler)

    empty_error_logger = logging.getLogger('empty_error')
    empty_error_handler = logging.FileHandler('empty.log')
    empty_error_logger.addHandler(empty_error_handler)

    print(f'Validating path {path}')
    for root, pat_id, fnames in os.walk(path):
        for file in fnames:
            filepath = os.path.join(root, file)
            if filepath.endswith('encounters.json'):

                with open(filepath, 'r') as f:
                    print(f"Validating {filepath}")
                    encounter_data = json.loads(f.read())
                    if not encounter_data:
                        empty_error_logger.error(filepath.split(os.sep)[-2])
                        continue
                    for item in encounter_data:
                        try:
                            # breakpoint()
                            value = item['file']
                        except (KeyError, TypeError) as e:
                            key_error_logger.error(f"{filepath.split(os.sep)[-2]} - {e}")
                            break
                        err = validate_enc(value)
                        if err:
                            encdate = value.get('encdate')
                            error_logger.error(f"{filepath.split(os.sep)[-2]}  - {encdate} -  {err}")
                            print(f"Validation err in {filepath.split(os.sep)[-2]}")
                            # breakpoint()
                            break
                            
