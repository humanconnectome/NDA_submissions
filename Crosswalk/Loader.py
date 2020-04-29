import pandas as pd
import types


class Loader:
    # def __init__(self, post=None):
    #     if post is not None:
    #         self.post_hook = types.MethodType(post, self)
    #
    # def post_hook(self, df):
    #     return df

    def __init__(self, name):
        self.name = name
        self.setup()

    def setup(self):
        # load datadictionaries or any other file that will aid in interpreting fields
        # for creating shadow dataframe later on
        pass

    def get_source_name(self):
        return self.name

    def _fields_hook_(self, fields):
        # add any special fields that are not explicity stated in yaml map files
        return fields

    def _load_hook_(self, fields):
        # Implement actual loading of data
        return pd.DataFrame()

    def _post_load_hook_(self, df):
        # Merge additional data sources or manipulate the dataframe to create additional fields
        return df

    def _detect_missing_fields_hook_(self, df, fields):
        # From the fields requested, which fields are missing/unavailable
        return fields

    def _create_shadow_dataframe(df, fields):
        # Create a shadow dataframe with alternatives for field (like text instead of internal code)
        return df.copy(), df.copy()

    def load(self, fields):
        fields = self._fields_hook_(fields)
        df = self._load_hook_(fields)
        df = self._post_load_hook_(df)
        self._detect_missing_fields_hook_(df, fields)
        df, DF = self._create_shadow_dataframe(df, fields)
        return df, DF
