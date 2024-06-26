import os
import io
import pandas as pd
import requests
from ccf.box import CachedBox
from ccf.easy_yaml import EasyYaml
from ccf.redcap import CachedRedcap
from ccf.config import LoadSettings

config = LoadSettings()

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
        described in the yaml map files. (names not renames)
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
        print("you are here")
        config = LoadSettings()
        filename = config['rosetta']['filename']
        print(filename)
        rosetta=pd.read_csv(filename)
        rosetta = rosetta[['REDCap_id','subject', 'redcap_event','pseudo_guid', 'M/F', 'nda_interview_date', 'nda_age']]
        rosetta.columns = ['id','subject', 'redcap_event','subjectkey', 'gender', 'interview_date', 'interview_age']
        df = rosetta.merge(df, on=['subject','redcap_event'], suffixes=('', '_alt'))
        df['source'] = self.name

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
        additional_fields = self._fields_hook_(fields)
        print("fields:",len(additional_fields))
        df = self._load_hook_(additional_fields)
        df = self._post_load_hook_(df)
        self._detect_missing_fields_hook_(df, fields)
        df, DF = self._create_shadow_dataframe(df, fields)
        df = df.replace('nan', pd.NA)
        DF = DF.replace('nan', '').fillna('')
        print('Shape of loaded data',df.shape)
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
        fromnames = LoadSettings()['Redcap']['datasources'][self.get_source_name()]['events']
        df = df[df.assessment.isin(fromnames)]
        df = df.rename(columns={"subid": "subject"})
        df['redcap_event']=df.assessment
        return super()._post_load_hook_(df)


class BoxHcdLoader(BoxLoader) :
    def _post_load_hook_(self, df):
        df = super()._post_load_hook_(df)
        df = df[df.subject.str.startswith('HCD', False)]
        return df


class BoxHcaLoader(BoxLoader) :
    def _post_load_hook_(self, df):
        df = super()._post_load_hook_(df)
        df = df[df.subject.str.startswith('HCA', False)]
        return df


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
        renames = LoadSettings()['Redcap']['datasources'][self.get_source_name()]['event_names']
        fromnames = LoadSettings()['Redcap']['datasources'][self.get_source_name()]['events']
        a = dict(zip(fromnames, renames))
        df["redcap_event"] = df['redcap_event_name'].map(a)
        backfill = df.loc[df.redcap_event == 'V1'][['id', 'subject']] #only V1 has subject identifiers
        df = pd.merge(df.drop(columns='subject'), backfill, how='left', on='id')
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


class ParentLoader(RedcapLoader):
    def __init__(self, name, definitions_dir="./definitions/"):
        super().__init__('parent', definitions_dir)

    def _fields_hook_(self, fields):
        return fields + ['child_id']

    def _post_load_hook_(self, df):
        df = df \
            .drop(columns=['subjectid']) \
            .rename(columns={'child_id': 'subjectid'})

        df[['subject', 'flagged']] = df.subjectid.str.split('_', 1, expand=True)

        # remove withdrawn
        df = df[df.flagged.isna()]

        return super()._post_load_hook_(df)


class QintLoader(RedcapLoader):
    def __init__(self, definitions_dir="./definitions/"):
        super().__init__('qint', definitions_dir)

    def _fields_hook_(self, fields):
        return fields + ['subjectid', 'visit']

    def _load_hook_(self, fields):
        redcap = CachedRedcap()
        exclude = ['subject', 'subjectkey', 'gender', 'interview_date', 'interview_age']
        fields = [x for x in fields if x not in exclude]
        df = redcap(self.get_source_name(), fields)
        renames = LoadSettings()['Redcap']['datasources'][self.get_source_name()]['event_names']
        fromnames = LoadSettings()['Redcap']['datasources'][self.get_source_name()]['visit']
        a = dict(zip(list(map(str, fromnames)), renames))
        df["redcap_event"] = df['visit'].map(a)
        return df

    def _post_load_hook_(self, df):
        visit = config['Redcap']['datasources'][self.get_source_name()]['visit']
        df = df[df.visit.isin(list(map(str, visit)))]
        df = df.rename(columns={"subjectid": "subject"})
        return super()._post_load_hook_(df)

    
class QintHcdLoader(QintLoader) :
    def _post_load_hook_(self, df):
        df = df[df.subjectid.str.startswith('HCD', False)]
        return super()._post_load_hook_(df)


class QintHcaLoader(QintLoader) :
    def _post_load_hook_(self, df):
        df = df[df.subjectid.str.startswith('HCA', False)]
        return super()._post_load_hook_(df)


class KsadsLoader(RedcapLoader):
    def __init__(self, definitions_dir="./definitions/"):
        super().__init__('ksads', definitions_dir)

    def _fields_hook_(self, fields):
        return fields + ['patientid']

    def _load_hook_(self, fields):
        redcap = CachedRedcap()
        exclude = ['subject', 'subjectkey', 'gender', 'interview_date', 'interview_age']
        fields = [x for x in fields if x not in exclude]
        df = redcap(self.get_source_name(), list(fields))
        return df

    def _post_load_hook_(self, df):
        visit = config['visit']
        df = df[df.patientid.str.contains("V"+visit)]
        df['subject']=df.patientid.str[:10]
        
        return super()._post_load_hook_(df)


class SsagaLoader(RedcapLoader):
    def __init__(self, definitions_dir="./definitions/"):
        super().__init__('ssaga', definitions_dir)

    def _fields_hook_(self, fields):
        return fields + ['hcpa_id']

    def _load_hook_(self, fields):
        redcap = CachedRedcap()
        exclude = ['subject', 'subjectkey', 'gender', 'interview_date', 'interview_age']
        fields = [x for x in fields if x not in exclude]
        df = redcap(self.get_source_name(), list(fields))
        return df

    def _post_load_hook_(self, df):
        df = df.rename(columns={"hcpa_id": "subject"})
        return super()._post_load_hook_(df)
