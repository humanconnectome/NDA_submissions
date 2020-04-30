import pandas as pd
import types


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
