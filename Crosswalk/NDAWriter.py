import subprocess
from os import path

import yaml
import pandas as pd
import re
import os

from IPython.core.display import display

trailing_zero_rx = re.compile('(\d+)\.0(?!\d)')
pattern = re.compile('Validation report output to: (.+?csv)\n')

pathstructuresout = "./prepped_structures"


def save_df(structure, df):
    #     filepath = f'{pathstructuresout}/HCPD_{structure}_{snapshotdate}.csv'
    filepath = f'{pathstructuresout}/HCPD_{structure}.csv'
    root, num = structure[:-2], structure[-2:]

    with open(filepath, 'w') as fd:
        fd.write('{},{:d}\n'.format(root, int(num)))
        output = df.to_csv(index=False)
        #         output = trailing_zero_rx.sub('\\1', output)
        fd.write(output)


# %%
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
        print(f'Field "{field.name}" has the following invalid values:', set(field[~valid]))
        print(f"Dropping {(~valid).sum()} values.")
        field = field.where(valid)
    return field


def validate_integer(definition, field):
    #             field_series = field_series.astype('Int64',errors='ignore')
    field = pd.to_numeric(field, 'coerce')
    if field.dtype == 'Float64':
        field = field.round().astype('Int64')
    field = validate_numbers_in_range(definition, field)
    return field


# %%

def validate_float(definition, field):
    field = pd.to_numeric(field, 'coerce')
    #             if field.dtype == 'Float64':
    #                 field = field.round().astype('Int64')
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
        print(f'Field "{field.name}" has the following invalid values:', set(field[~valid]))

        print(f'Dropping {(~valid).sum()} values.')
        field = field.where(valid)

    return field


def validate_string(definition, field):
    # fillna("") is necessary else NaN will get converted to the string "nan" rather than blank strings
    field = field.fillna("").astype(str)
    max_length = definition.get('length')
    actual_length = field.str.len().max()
    if actual_length > max_length:
        print(f'Field "{field.name}" has a max length of {max_length}, but has data of length up to {actual_length}')

    field = validate_string_matches_range(definition, field)

    return field


def validate_guid(definition, field):
    valid = field.map(lambda value: value.startswith('NDAR'))
    if (~valid).any():
        print(f'Field "{field.name}" has incorrectly formatted GUID values:', set(field[~valid]))

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
    def __init__(self, validator="/home/m/.virtualenvs/ccf/bin/vtcmd"):
        self.validate_exec = validator
        self.nda_elements = {}
        self.reload_definitions()
        self.directory = './nda/'

    def load_struct(self, struct):
        filename = path.join(self.directory, struct + '.yaml')
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
        missing = [name for name, v in self.nda(struct) \
                   if v.get('required') and name not in df]
        if missing:
            print(f"{struct} is missing the fields: ", missing)

    def write(self, db):
        for struct, struct_elements in self.nda_elements.items():
            nda_defs = {x['name']: x for x in struct_elements}
            if struct not in db:
                continue
            df = db[struct]
            print('Entering ', struct)

            self.has_required_fields(struct, df)

            for name, field_series in df.iteritems():
                if name not in nda_defs:
                    print('Skipping', name)
                    continue
                dd = nda_defs[name]
                fieldtype = dd['type']
                #     print(name, s)
                df[name] = validations[fieldtype](dd, field_series)
            save_df(struct, df)

    def validate(self, filename):
        if '/' not in filename:
            filename = f'{pathstructuresout}/HCPD_{filename}.csv'

        output = subprocess.check_output(f'{self.validate_exec} {filename}', shell=True).decode()
        filename = pattern.search(output)
        if filename:
            filename = filename.groups()[0]

            df = pd.read_csv(filename)
            df = df.drop(columns=['FILE', 'ID', 'STATUS', 'EXPIRATION_DATE'])

            if df.ERRORS == 'None':
                print('No errors!')
                return True
            else:
                display(df.groupby(['ERRORS', 'COLUMN']).RECORD.count())
                return df
