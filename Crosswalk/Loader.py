import os
import pandas as pd
from ccf.box import CachedBox
from ccf.easy_yaml import EasyYaml
from ccf.redcap import CachedRedcap


class Loader:

    def __init__(self, name):
        self.name = name
        self.setup()

    def setup(self):
        """
        Use this function to load data dictionaries or any other file that will
        aid in interpreting fields for creating shadow dataframes later on.
        """
        pass

    def get_source_name(self):
        return self.name

    def _fields_hook_(self, fields):
        """
        Use this function to add sepcial fields that are not explicitly
        described in the yaml map files.
        """
        return fields

    def _load_hook_(self, fields):
        """
        Implements the actual loading of the data.
        """
        return pd.DataFrame()

    def _post_load_hook_(self, df):
        """
        Manipulate the dataframe to create additional or rename existing fields.
        This is also a good place to merge additional data.
        """

        rosetta = pd.read_csv('UnrelatedHCAHCD_w_STG_Image_and_pseudo_GUID09_27_2019.csv')
        rosetta = rosetta[['subjectped', 'nda_guid', 'nda_gender', 'nda_interview_date', 'nda_interview_age']]
        rosetta.columns = ['subject', 'subjectkey', 'gender', 'interview_date', 'interview_age']
        df = rosetta.merge(df, on='subject', suffixes=('', '_alt'))
        df['source'] = self.name
        df['age'] = df.interview_age / 12

        return df

    def _detect_missing_fields_hook_(self, df, fields):
        """
        Notify the user if any of the requested fields are missing or unavailable.
        """
        diff = set(fields).difference(df.columns)
        if diff:
            print(self.name, 'Some columns were unavailable: ', diff)

        return diff

    def _create_shadow_dataframe(self, df, fields):
        """
        Create a shadow dataframe which for example contains the text
        labels for coded fields.
        """
        return df.copy(), df.copy()

    def load(self, fields):
        """
        The main function that runs through all of the above functions in order.
        """
        fields = self._fields_hook_(fields)
        df = self._load_hook_(fields)
        df = self._post_load_hook_(df)
        self._detect_missing_fields_hook_(df, fields)
        df, DF = self._create_shadow_dataframe(df, fields)
        return df, DF


class BoxLoader(Loader):
    def __init__(self, name, boxid):
        self.boxid = boxid
        self.box = CachedBox(cache='./')
        super().__init__(name)

    def _load_hook_(self, fields):
        df = self.box.read_csv(self.boxid)
        return df

    def _post_load_hook_(self, df):
        df = df.rename(columns={"subid": "subject"})
        return super()._post_load_hook_(df)


class RedcapLoader(Loader):
    def __init__(self, name, definitions_dir="./definitions/"):
        self.directory = definitions_dir
        self.definitions = {}
        super().__init__(name)

    def setup(self):
        filename = os.path.join(self.directory, self.name + '.yaml')
        Y = EasyYaml()
        self.definitions = Y(filename)

    def _load_hook_(self, fields):
        redcap = CachedRedcap()
        df = redcap.get_behavioral(self.get_source_name(), list(fields))
        return df

    def _detect_missing_fields_hook_(self, df, fields):
        # Add checkbox fields
        extended_fieldslist = []
        for name in fields:
            d = self.definitions.get(name)
            if d and d['type'] == 'checkbox':
                extended_fieldslist.extend([f'{name}___{k}' for k, v in d['choices'].items()])
            else:
                extended_fieldslist.append(name)

        return super()._detect_missing_fields_hook_(df, extended_fieldslist)

    def _create_shadow_dataframe(self, df, fields):
        df = df.copy()
        DF = df.copy()

        for name in fields:
            if name not in self.definitions:
                # if not in data dictionary, then won't know how to manipulate so just skip
                continue

            field = self.definitions.get(name)

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
