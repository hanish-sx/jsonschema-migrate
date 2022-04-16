import json
import pathlib
import sys
from jsonschema import Draft7Validator, validate, ValidationError


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


def add_required_from(error: ValidationError):
    instance = error.instance
    schema = error.schema
    required_keys = error.validator_value
    # breakpoint()

    for key in required_keys:
        if key in instance:
            continue
        type_ = schema['properties'][key]['type']
        if isinstance(type_, list):
            type_ = next((v for v in type_), 'null')

        func = DEFAULT_VALUES.get(type_, 'null')
        instance[key] = func(None)
        



def fix_type_from(error: ValidationError):
    ...


if __name__ == '__main__':
    BASE_PATH = pathlib.Path(__file__).parent

    iter_dir = BASE_PATH / sys.argv[1]
    out_dir = BASE_PATH / sys.argv[2]

    out_dir.mkdir(exist_ok=True, parents=True)


    for file_ in iter_dir.glob('**/*.json'):
        with open(file_) as f:
            encounter_data = json.load(f)

        fix_data = []
        for enc in encounter_data:
            v = Draft7Validator(schema=encounter_schema, format_checker=format_checker)
            for error in sorted(v.iter_errors(enc['file']), key=lambda e: e.schema_path):
                print(error.message)
                if error.validator == 'required':
                    add_required_from(error)
                # elif error.validator == 'type':
                #     fix_type_from(error)
            fix_data.append(enc)
        parts = list(file_.parts)
        parts[-3] = out_dir.stem
        new_path = pathlib.Path(*parts)
        new_path.parent.mkdir(exist_ok=True, parents=True)
        with open(new_path, 'w') as f:
            json.dump(fix_data, f)
        print('.', end='', flush=True)
    print()
