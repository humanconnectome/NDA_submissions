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
def in_range_str(value_range):
    def closure_fn(value):
        if value == '' or pd.isna(value):
            return True
        if type(value) is not str:
            value = str(value)
        for rng in value_range:
            if str(rng) == value:
                return True
            elif rng == 'NDAR*' and value.startswith('NDAR'):
                return True
        return False
    return closure_fn


def in_range_num(value_range):
    def closure_fn(value):
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
    return closure_fn


# %%

class NDAWriter:
    def __init__(self, validator = "/home/m/.virtualenvs/ccf/bin/vtcmd"):
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

    def nda(self):
        return {struct: {x['name']: x for x in struct_elements} for struct, struct_elements in self.nda_elements.items()}

    def write(self, db):
        for struct, struct_elements in self.nda_elements.items():
            nda_defs = {x['name']: x for x in struct_elements}
            if struct not in db:
                continue
            df = db[struct]
            print('Entering ', struct)

            required_fields = {k:v for k,v in nda_defs.items() if v.get('required')}
            missing_fields = [k for k, v in required_fields.items() if k not in df]
            if missing_fields:
                print('Missing fields: ', missing_fields)

            for name, field_series in df.iteritems():
                if name not in nda_defs:
                    print('Skipping', name)
                    continue
                dd = nda_defs[name]
                if 'range' in dd:
                    if dd['type'] in ['String', 'GUID']:
                        valid = field_series.map(in_range_str(dd['range']))
                    else:
                        valid = field_series.map(in_range_num(dd['range']))

                    if (~valid).any():
                        print(f'Field "{name}" has the following invalid values:', set(field_series[~valid]))
                #     print(name, s)
                if dd['type'] == 'String':
                    field_series = field_series.fillna("").astype(str)
                    df[name] = field_series
                    if field_series.dtype != 'O':
                        print('%s should be String, but is listed as %s' % (name, field_series.dtype))
                        continue
                    max_length = dd.get('length')
                    length = field_series.str.len().max()
                    if length > max_length:
                        print(f'Field "{name}" has a max length of {max_length}, but has data of length up to {length}')
                    pass
                elif dd['type'] == 'Integer':
                    #             field_series = field_series.astype('Int64',errors='ignore')
                    field_series = pd.to_numeric(field_series, 'coerce')
                    if field_series.dtype == 'Float64':
                        field_series = field_series.round().astype('Int64')
                    df[name] = field_series
                elif dd['type'] == 'Float':
                    field_series = pd.to_numeric(field_series, 'coerce')
                    #             if field_series.dtype == 'Float64':
                    #                 field_series = field_series.round().astype('Int64')
                    df[name] = field_series
                elif dd['type'] == 'GUID':
                    pass
                elif dd['type'] == 'Date':
                    pass
            #     break
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
