import os
import re
import subprocess
from os import path

import pandas as pd
import yaml
from IPython.core.display import display

from libs.YamlCache import YamlCache

trailing_zero_rx = re.compile('(\d+)\.0(?!\d)')
pattern = re.compile('Validation report output to: (.+?csv)\n')


def validate_numbers_in_range(definition, field):
    def range_filter(value):
        if pd.isna(value):
            return True
        value = pd.to_numeric(value)
        for rng in value_range:
            if type(rng) is str and '::' in rng:
                min_n, max_n = rng.split('::')
                if float(min_n) <= value <= float(max_n):
                    return True
            elif rng == value:
                return True
        return False

    if 'range' not in definition:
        return field

    value_range = definition['range']
    valid = field.map(range_filter)
    if (~valid).any():
        print(f'{field.name}: Invalid values ', set(field[~valid]))
        print(f"Dropping {(~valid).sum()} values.")
        field = field.where(valid)
    return field


def validate_integer(definition, field):
    field = pd.to_numeric(field, 'coerce')
    if field.dtype == 'Float64':
        field = field.round().astype('Int64')
    field = validate_numbers_in_range(definition, field)
    return field


def validate_float(definition, field):
    field = pd.to_numeric(field, 'coerce')
    field = validate_numbers_in_range(definition, field)
    return field


def validate_string_matches_range(definition, field):
    def range_filter(value):
        if value == '' or pd.isna(value):
            return True
        if type(value) is not str:
            value = str(value)
        for rng in value_range:
            if str(rng) == value:
                return True
        return False

    if 'range' not in definition:
        # return all values, no range check needed
        return field

    value_range = definition['range']
    valid = field.map(range_filter)
    if (~valid).any():
        print(f'{field.name}: Invalid values ', set(field[~valid]))

        print(f'Dropping {(~valid).sum()} values.')
        field = field.where(valid)

    return field


def validate_string(definition, field):
    # fillna("") is necessary else NaN will get converted to the string "nan" rather than blank strings
    field = field.fillna("").astype(str)

    # check specified length is long enough
    max_length = definition.get('length')
    actual_length = field.str.len().max()
    if actual_length > max_length:
        print(f'{field.name}: Increase length from {max_length} --> {actual_length} ')

    # check range
    field = validate_string_matches_range(definition, field)

    return field


def validate_guid(definition, field):
    valid = field.map(lambda value: value.startswith('NDAR'))
    if (~valid).any():
        print(f'{field.name}: Incorrectly formatted GUID values:', set(field[~valid]))

    return field.where(valid)


def validate_date(definition, field):
    return field


validations = {
    'Integer': validate_integer,
    'Float': validate_float,
    'String': validate_string,
    'GUID': validate_guid,
    'Date': validate_date
}


class NDAWriter:
    def __init__(self, definitions_dir="./nda", completed_dir='./prepped_structures/',
                 validator="/home/m/.virtualenvs/ccf/bin/vtcmd"):
        self.y = YamlCache()
        self.nda_elements = {}
        self.validate_exec = validator
        self.directory = definitions_dir
        self.reload_definitions()
        self.completed_path = completed_dir

    def load_struct(self, struct):
        filename = path.join(self.directory, struct + '.yaml')
        elements = self.y.load(filename)
        self.nda_elements[struct] = elements
        return self

        if path.exists(filename):
            with open(filename, 'r') as fd:
                self.nda_elements[struct] = yaml.load(fd, yaml.SafeLoader)
        return self

    def reload_definitions(self):
        for filename in os.listdir(self.directory):
            struct = filename[:-5]
            self.load_struct(struct)
        return self

    def nda(self, struct):
        if struct not in self.nda_elements:
            raise Exception(f"{struct} is not defined in NDA definitions.")
        elements = self.nda_elements[struct]
        return {x['name']: x for x in elements}

    def has_required_fields(self, struct, df):
        missing = [name for name, v in self.nda(struct).items() \
                   if v.get('required') and name not in df]
        if missing:
            print(f"{struct} is missing the fields: ", missing)

    def validate_struct(self, struct, df):
        self.has_required_fields(struct, df)
        df = df.copy()
        nda_defs = self.nda(struct)
        for name, field in df.iteritems():
            if name not in nda_defs:
                print(f"{name}: Field not pre-defined, skipping validation.")
            else:
                definition = nda_defs[name]
                field_type = definition['type']

                # validate by field type
                df[name] = validations[field_type](definition, field)
        return df

    def write(self, struct, df):
        print(f'For struct "{struct}": ')
        df = self.validate_struct(struct, df)

        filepath = path.join(self.completed_path, struct + '.csv')
        root, num = struct[:-2], struct[-2:]
        with open(filepath, 'w') as fd:
            fd.write('{},{:d}\n'.format(root, int(num)))
            output = df.to_csv(index=False)
            fd.write(output)

    def write_all(self, db):
        for struct, struct_elements in self.nda_elements.items():
            if struct not in db:
                continue
            df = db[struct]
            self.write(struct, df)

    def validate(self, struct):
        filename = path.join(self.completed_path, struct + '.csv')
        if not path.exists(filename):
            print("File does not exist. Aborting.")
            return

        output = subprocess.check_output(f'{self.validate_exec} {filename}', shell=True).decode()
        filename = pattern.search(output)
        if filename:
            filename = filename.groups()[0]

            df = pd.read_csv(filename)
            df = df.drop(columns=['FILE', 'ID', 'STATUS', 'EXPIRATION_DATE'])

            if len(df) == 1 and df.ERRORS.iloc[0] == 'None':
                print('No errors!')
                return True
            else:
                display(df.groupby(['ERRORS', 'COLUMN']).RECORD.count())
                return df
