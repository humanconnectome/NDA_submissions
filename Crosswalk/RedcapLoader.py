from os import path
import pandas as pd
from ccf.easy_yaml import EasyYaml
from ccf.redcap import get_behavioral

source_map = {
    'child': 'hc.pkl',
    'parent': 'hp.pkl',
    'teen': 'ht.pkl'
}

def parent2child(df, keep_withdrawn=False):
    df = df \
        .drop(columns=['subjectid']) \
        .rename(columns={'child_id': 'subjectid'})

    df[['subject','flagged']] = df.subjectid.str.split('_', 1, expand=True)

    if not keep_withdrawn:
        df = df[df.flagged.isna()]

    return df


class RedcapLoader:

    def __init__(self, name, definitions_dir="./definitions/"):
        self.name = name
        self.Y = EasyYaml()
        self.directory = definitions_dir
        self.dd = {}
        self.load_definitions()

        # load data dictionary
        # with open('redcap/redcap.pkl', 'rb') as fd:
        #     self.dd = pickle.load(fd)[self.name]

    def load_definitions(self):
        filename = path.join(self.directory, self.name + '.yaml')
        self.dd = self.Y(filename)

    def get_source_name(self):
        return self.name

    def add_checkbox(self, names):
        result = []
        for name in names:
            d = self.dd.get(name)
            if d and d['type'] == 'checkbox':
                result.extend([f'{name}___{k}' for k, v in d['choices'].items()])
            else:
                result.append(name)
        return result

    def load(self, fields):
        to_get = list(fields)
        to_get = self.add_checkbox(fields)
        fields = list(fields)
        # to_get.append('interview_age')
        if self.get_source_name() == 'parent':
            fields += ['child_id']
        df = get_behavioral(self.get_source_name(), fields)
        if self.get_source_name() == 'parent':
            df = parent2child(df)

        rosetta = pd.read_csv('UnrelatedHCAHCD_w_STG_Image_and_pseudo_GUID09_27_2019.csv')
        rosetta = rosetta[['subjectped', 'nda_guid']]
        rosetta.columns = ['subject', 'subjectkey']
        df = rosetta.merge(df, on='subject')
        diff = set(to_get).difference(df.columns)
        if diff:
            print(self.name, 'Some columns were unavailable: ', diff)
            for x in diff:
                to_get.remove(x)

        # df = df[set(to_get)]

        # df = df[df.columns[df.columns.isin(fields)]]
        df['source'] = self.name
        df['age'] = df.interview_age / 12
        return self.manipulate(df, fields)

    def manipulate(self, df, fields):
        df = df.copy()
        DF = df.copy()

        for name in fields:
            if name not in self.dd:
                # if not in data dictionary, then won't know how to manipulate so just skip
                continue

            field = self.dd.get(name)

            if field['type'] == 'checkbox':
                replace_with_code = {f'{name}___{k}': k for k, v in field['choices'].items()}
                replace_with_value = {f'{name}___{k}': v for k, v in field['choices'].items()}

                z = df[replace_with_code.keys()].stack()
                z = z[z == 1].reset_index(level=1).rename(columns={'level_1': name}).drop(columns=0)

                x = z.replace(replace_with_value).groupby(level=0).agg(lambda values: '; '.join(values))
                X = z.replace(replace_with_code).groupby(level=0).agg(lambda values: '; '.join(values))

            elif name in df:
                x = df[name].copy()
                if field['type'] in ['radio', 'dropdown']:
                    X = x.replace({float(k): v for k, v in field['choices'].items()})
                elif field['type'] in ['text']:
                    X = x.astype(str)
                else:
                    X = x.copy()
            else:
                x = pd.Series()
                X = pd.Series()
            df[name] = x
            DF[name] = X

        return df, DF



