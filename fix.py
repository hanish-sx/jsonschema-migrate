import ast
import collections
import json
import pathlib
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError
import glom

from schema2 import encounter_schema, format_checker


def fix_object(x):
    # breakpoint()
    if isinstance(x, list):
        return next((o for o in x), {})
    elif x == '[]':
        return {}
    return x

DEBUG = False

DEFAULT_VALUES = {
    'string': lambda x: ''.join(x) if isinstance(x, collections.abc.Container) else str(x),
    'array': lambda x: [x],
    'null': lambda x: None,
    'object': lambda x: next((o for o in x), {}) if isinstance(x, list) else x,
    # 'object': fix_object,
    'number': 0,
    'non_empty_string': lambda x: '<placeholder for non empty string>',
    'misc': str,
}

def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]
    validate_type = validator_class.VALIDATORS["type"]
    validate_required = validator_class.VALIDATORS["required"]

    def set_defaults(validator, properties, instance, schema):
        if DEBUG:
            print('*'*10, 'properties')
            print(f"{validator=}")
            print(f"{properties=}")
            print(f"{instance=}")
            print(f"{schema=}")
        # if we can provide default value in our schema, we can probably use this
        # mainly for `reason_for_referral` atm
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            if error.validator in ['required']:
                continue # skip since we already do fix `required` keys in below function

            validator_value = error.validator_value
            if isinstance(validator_value, list):
                validator_value = next((value for value in validator_value), 'null')
            if isinstance(validator_value, dict):
                validator_value = 'object'
            elif error.validator in ['minItems']:
                validator_value = 'misc'
            
            try:
                default_value =  DEFAULT_VALUES.get(validator_value)
                glom.assign(instance, '.'.join(str(x) for x in error.path), default_value(error.instance))
            except TypeError as e:
                raise
            yield error


    # def set_proper_type(validator, type_, instance, schema):
    #     print('*'*10, 'type')
    #     print(f"{validator=}")
    #     print(f"{type_=}")
    #     print(f"{instance=}")
    #     print(f"{schema=}")

    #     for error in validate_type(validator, type_, instance, schema):
    #         print(f'type error: {error}')
    #         # instance.setdefault()
    #         breakpoint()
    #         error.instance = ' '.join(instance)
    #         yield error


    def set_required_keys(validator, keys, instance, schema):
        if DEBUG:
            print('*'*10, 'required')
            print(f"{validator=}")
            print(f"{keys=}")
            print(f"{instance=}")
            print(f"{schema=}")

        for error in validate_required(validator, keys, instance, schema):
            key = error.message.partition(" ")[0].strip("'")
            type_ = schema['properties'][key]['type']
            if isinstance(type_, list):
                type_ = next((value for value in type_), 'null')
            if isinstance(type_, dict):
                type_ = 'object'
            try:
                default_value =  DEFAULT_VALUES.get(type_)
            except TypeError as e:
                # breakpoint()
                raise

            if "'date' is a required property" in error.message:
                breakpoint()

            # `ehr_id` and `enc_type` can't be None according to schema
            if key in ["ehr_id", "enc_type"]:
                instance[key] = "NA"
            elif key == "patient_id":
                # trying to fix as much as we could.
                # hack to get the patient id from the filename
                # don't do this...usually
                import sys
                frame = sys._getframe(10) # why 10 ? i don't know :), i manually checked and found it was 10, could have been 11, 12 or who knows even 20
                # we will get the file name like
                # `PosixPath('test_dump/06a34afd0d292aec2fdd92334f8a160e114ccbe72c17121addea38ac6df01ab3/encounters.json')`
                # from this we can just get the stem
                # which will be the patient_id. Need to make sure, otherwise patient_id will be wrong, 
                # and incorrect data is *worser* than no data
                fname = frame.f_globals.get('file')
                patient_id = fname.parent.stem
                instance[key] = patient_id
            else:
                instance[key] = default_value(None)
            yield error


    return validators.extend(
        validator_class,
        {
            "properties": set_defaults,
            #  "type": set_proper_type,
            "required": set_required_keys
        },
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


if __name__ == '__main__':
    # data_dir = pathlib.Path(__file__).parent / 'patient_dump'
    data_dir = pathlib.Path(__file__).parent / 'new_files_w_err'

    encounter_files = data_dir.glob('**/encounters.json')

    new_dump_dir = data_dir.parent / 'new_dump1'
    new_dump_dir.mkdir(exist_ok=True)

    for file in encounter_files:
        # print(file)
        if '13e145f6628cdaab1204cfa0a5306ebe98c9bfb6b2b87c18da2418be291d11b9' in str(file):
            breakpoint()
        with open(file) as f:
            fixed_data = []
            data = json.load(f)
            for enc in data:
                v = DefaultValidatingDraft7Validator(schema=encounter_schema, format_checker=format_checker)
                errors = sorted(v.iter_errors(enc['file']), key=lambda e: e.path)
                try:
                    # DefaultValidatingDraft7Validator(schema=encounter_schema, format_checker=format_checker).validate(enc["file"])
                    v.validate(enc['file'])
                except ValidationError as e:
                    # breakpoint()
                    print(e.message, e.path)
                    # pass
                fixed_data.append(enc)
        parts = list(file.parts)
        parts[-3] = 'new_dump'
        new_path = pathlib.Path(*parts)
        new_path.parent.mkdir(exist_ok=True)
        with open(new_path, 'w') as f:
            # json.dump(fixed_data, f, default=str)
            json.dump(fixed_data, f)
        print('.', end='', flush=True)
    print()
