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
        return df

    def _detect_missing_fields_hook_(self, df, fields):
        """
        Notify the user if any of the requested fields are missing or unavailable.
        """
        return fields

    def _create_shadow_dataframe(df, fields):
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
