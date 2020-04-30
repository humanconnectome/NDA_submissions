import pandas as pd

from ccf.redcap import CachedRedcap


class QintLoader:

    def __init__(self):
        self.name = "qint"

    def get_source_name(self):
        return self.name

    def load(self, fields):
        fields = list(fields)
        fields.append("subjectid")
        to_get = fields
        redcap = CachedRedcap()
        df = redcap(self.name, fields)
        rosetta = pd.read_csv('UnrelatedHCAHCD_w_STG_Image_and_pseudo_GUID09_27_2019.csv')
        rosetta = rosetta[['subjectped', 'nda_guid', 'nda_interview_age', 'nda_interview_date', 'nda_gender']]
        rosetta.columns = ['subject', 'subjectkey', 'interview_age', 'interview_date', 'gender']
        df = rosetta.merge(df, left_on='subject', right_on='subjectid')

        diff = set(to_get).difference(df.columns)
        if diff:
            print(self.name, 'Some columns were unavailable: ', diff)
            for x in diff:
                to_get.remove(x)


        return df.copy(), df.copy()
