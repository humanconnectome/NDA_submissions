import pandas as pd

from ccf.box import CachedBox


class BoxLoader:

    def __init__(self, name, boxid=None):
        self.name = name
        self.boxid = boxid
        self.box = CachedBox(cache='./')

    def get_source_name(self):
        return self.name

    def load(self, fields):
        to_get = fields
        df = self.box.read_csv(self.boxid)
        rosetta = pd.read_csv('UnrelatedHCAHCD_w_STG_Image_and_pseudo_GUID09_27_2019.csv')
        rosetta = rosetta[['subjectped', 'nda_guid', 'nda_interview_age', 'nda_interview_date', 'nda_gender']]
        rosetta.columns = ['subject', 'subjectkey', 'interview_age', 'interview_date', 'gender']
        df = rosetta.merge(df, left_on='subject', right_on='subid')

        diff = set(to_get).difference(df.columns)
        if diff:
            print(self.name, 'Some columns were unavailable: ', diff)
            for x in diff:
                to_get.remove(x)

        df = df[set(to_get)]

        return df.copy(), df.copy()
