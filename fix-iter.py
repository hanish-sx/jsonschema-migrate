import copy
import json
import pathlib
import re
import sys
import collections.abc


from jsonschema import Draft7Validator, validate, ValidationError, validators
import glom


from schema2 import encounter_schema, format_checker



DEFAULT_VALUES = {
    'string': lambda x: ''.join(str(v) for v in x) if isinstance(x, collections.abc.Container) else str(x),
    'array': lambda x: [x],
    'null': lambda x: None,
    'object': lambda x: next((o for o in x), {}) if isinstance(x, list) else x,
    # 'object': fix_object,
    'number': lambda x: float(x or 0),
    'non_empty_string': lambda x: '<placeholder for non empty string>',
    'misc': str,
}

TYPES = {
    'string': str,
    'object': dict,
    'array': list,
    'number': (int, float),
    'null': type(None),
}

def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]
    validate_required = validator_class.VALIDATORS["required"]

    def set_defaults(validator, properties, instance, schema):
        # if we can provide default value in our schema, we can probably use this
        # mainly for `reason_for_referral` atm
        for property, subschema in properties.items(): # shouldn't hit
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            for property, subschema in properties.items():
                # if "default" in subschema and error.path[0] == property:
                # really trying to target `documentation_of` which i shouldn't do actually
                if "default" in subschema and error.path[0] == property and len(error.path) <= 2:
                    if property == 'description':
                        breakpoint()
                    instance[property] = copy.deepcopy(subschema["default"])
            # if error.validator in ['required', 'minItems',]:
            if error.validator in ['minItems',]:
                print('*err', error.message)
                continue # skip since we already do fix `required` keys in below function

            if error.validator == 'required':
                breakpoint() # shoudln't hit here
                continue

            if error.validator == 'type':
                # handle particular case for `phone`,
                # because the change was to create a nested object
                if error.path[0] == 'phone':
                    if re.search(r'(\'\(\d+\)\s\d+.*)|(\d+-\d+-\d+.*)', error.message):
                        instance['phone'] = {'home': error.instance or 'no data found'}
                    elif error.message == "None is not of type 'object'":
                        instance['phone'] = {'home': error.instance or 'no data found'}
                    elif re.search(r".* is not of type 'object'", error.message):
                        instance['phone'] = {'home': error.instance or 'no data found'}
                    continue
                else:
                    validator_value = error.validator_value
                    if isinstance(validator_value, list):
                        validator_value = next((value for value in validator_value), 'null')
                    if isinstance(validator_value, dict):
                        validator_value = 'object'
                    elif error.validator in ['minItems']:
                        validator_value = 'misc'
                    
                    try:
                        default_value =  DEFAULT_VALUES.get(validator_value)
                        # if type error.instance is error.validator which will be
                        # eg: `{}` `object`, then only we will update it
                        # the case was particularly for `documentation_of` which had a default value, but the instance had `'[]'`
                        # for some reason 
                        if isinstance(error.instance, TYPES.get(error.validator_value)):
                            glom.assign(instance, '.'.join(str(x) for x in error.path), default_value(error.instance))
                    except TypeError as e:
                        raise

                continue
            elif error.validator == 'anyOf':
                try:
                    if error.instance is None:
                        anyOf_type = next(o for o in error.validator_value)['type']
                        func = DEFAULT_VALUES.get(anyOf_type)
                        if schema['properties'].get('default') is None:
                            glom.assign(instance, '.'.join(str(x) for x in error.path), func(error.instance))
                # except TypeError as e:
                except Exception as e:
                    breakpoint()
                    e
                    raise

            # else:
            #     ...
            #     # breakpoint()

            yield error

    def set_min_items(validator, min_length, instance, schema):
        breakpoint()
        if 'default' in schema:
            # we will extend and see if we get any maxItems error
            instance.extend(schema['default'])


    def set_additional_properties(validator, aP, instance, schema):
        type_ = aP['type']
        func =  DEFAULT_VALUES.get(type_)
        for key, value in instance.items():
            instance[key] = func(value)

    def set_required_keys(validator, keys, instance, schema):
        for error in validate_required(validator, keys, instance, schema):
            for key in keys:
                if key in instance:
                    continue
                try:
                    type_ = schema['properties'][key]['type']
                except KeyError as e:
                    raise
                if isinstance(type_, list):
                    type_ = next((value for value in type_), 'null')
                if isinstance(type_, dict):
                    type_ = 'object'
                try:
                    default_value =  DEFAULT_VALUES.get(type_)
                except TypeError as e:
                    raise

                # `ehr_id` and `enc_type` can't be None according to schema
                if key in ["ehr_id", "enc_type"]:
                    instance[key] = "NA"
                elif key == "patient_id":
                    # trying to fix as much as we could.
                    # hack to get the patient id from the filename
                    # don't do this...usually
                    # breakpoint()
                    import sys
                    frame = sys._getframe(11) # why 11 ? i don't know :), i manually checked and found it was 10, could have been 11, 12 or who knows even 20
                    # we will get the file name like
                    # `PosixPath('test_dump/06a34afd0d292aec2fdd92334f8a160e114ccbe72c17121addea38ac6df01ab3/encounters.json')`
                    # from this we can just get the stem
                    # which will be the patient_id. Need to make sure, otherwise patient_id will be wrong, 
                    # and incorrect data is *worser* than no data
                    fname = frame.f_globals.get('file_')
                    patient_id = fname.parent.stem
                    instance[key] = patient_id
                    # print(f'{fname=}')
                else:
                    try:
                        instance[key] = default_value(None)
                    except TypeError as e:
                        raise
            # yield error # commenting this is required, but need to figure out why



    return validators.extend(
        validator_class,
        {
            "properties": set_defaults,
            #  "type": set_proper_type,
            #  "type": set_defaults,
            "required": set_required_keys,
            # "minItems": set_min_items,
            # "anyOf": set_any_of,
            # "format": set_format,
            "additionalProperties": set_additional_properties,
        },
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


if __name__ == '__main__':
    BASE_PATH = pathlib.Path(__file__).parent

    iter_dir = BASE_PATH / sys.argv[1]
    out_dir = BASE_PATH / sys.argv[2]
    out_dir.mkdir(exist_ok=True)

    for file_ in iter_dir.glob('**/*.json'):
        with open(file_) as f:
            encounter_data = json.load(f)
        fix_data = []
        for enc in encounter_data:
            try:
                v = DefaultValidatingDraft7Validator(schema=encounter_schema, format_checker=format_checker)
                v.validate(enc['file'])
            except ValidationError as e:
                # breakpoint()
                print(e.message)
            fix_data.append(enc)
        if sys.argv[3]:   
            parts = list(file_.parts)
            parts[-3] = out_dir.stem
            new_path = pathlib.Path(*parts)
            new_path.parent.mkdir(exist_ok=True)
            with open(new_path, 'w') as f:
                json.dump(fix_data, f)
            print('.', end='', flush=True)
    print()
