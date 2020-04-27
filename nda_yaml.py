import requests
import pandas as pd
import os
import re
import io
import numpy as np
from ccf.easy_yaml import EasyYaml

Y = EasyYaml()
number_range_rx = re.compile('([0-9.-]+) *:: *([0-9.-]+)')
split_eq = re.compile('(?: |^|\\b)([0-9\.\-]{1,7}|[a-zA-Z]{1,3}) *= *(.+?)(?=;|$)', re.DOTALL)
column_renames = {
    'Condition': 'condition',
    'ElementName': 'name',
    'DataType': 'type',
    'Size': 'length',
    'Required': 'required',
    'ElementDescription': 'description',
    'ValueRange': 'range',
    'Notes': 'notes',
    'Aliases': 'alias'}


def num(x):
    n = pd.to_numeric(x, 'ignore')
    if type(n) is np.int64:
        return int(n)
    elif type(n) is np.float64:
        return float(n)
    return n.strip()


def split_range(x):
    z = []
    if pd.isna(x):
        return None

    for i in x.split(';'):
        result = number_range_rx.search(i)
        if result:
            z.append('::'.join(list(map(str, list(map(num, result.groups()))))))
        else:
            z.append(num(i))
    return z


def split_codes(notes):
    if pd.isna(notes):
        return None
    r = {num(k): v.strip() for k, v in split_eq.findall(notes)}
    if r:
        return r


def get_struct(structure):
    r = requests.get(f'https://nda.nih.gov/api/datadictionary/v2/datastructure/{structure}/csv')
    if r.status_code == 200:
        z = pd.read_csv(io.BytesIO(r.content))
        return z
    else:
        raise Exception(f"The structure '{structure}' does not exist in the NDA.")


def download(struct, dest="./nda"):
    """
    Download an NDA structure as a yaml file into dest.
    :param struct:
    :param dest:
    :return:
    """

    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)

    df = get_struct(struct)
    df = df.rename(columns=column_renames)
    # required field conv
    df.loc[df.required == 'Recommended', 'required'] = None
    df.loc[df.required == 'Required', 'required'] = True

    df['codes'] = df.notes.map(split_codes)
    df.range = df.range.map(split_range)

    simple_list = [{k: v for k, v in x.items() if type(v) is list or pd.notna(v)} for x in df.to_dict('records')]
    for i in simple_list:
        if 'length' in i:
            i['length'] = int(i['length'])
    simple_list = {x.pop('name'): x for x in simple_list}
    filename = os.path.join(dest, struct + '.yaml')
    Y.write(filename, simple_list)
    return simple_list
