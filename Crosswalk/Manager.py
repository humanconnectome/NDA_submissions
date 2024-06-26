import pandas as pd
from collections.abc import Iterable

class Manager:
    def __init__(self, data=None, writer=None, transformer=None):
        self.data = data
        self.writer = writer
        self.transformer = transformer


    def preload_data(self, sources=None):
        """
         Preload the data from the datacache.
        :param sources: If None, all sources will be loaded. Otherwise, a list of sources to load.
        :return:
        """
        if sources is None:
            sources = self.writer.sources.keys()
        elif isinstance(sources, str):
            sources = [sources]
        elif not isinstance(sources, Iterable):
            raise ValueError('Sources must be a string or iterable of strings.')
        unique = self.transformer.get_unique_variables() #these are names (not renames) in maps

        # filter out the unique variables not included in the `sources`
        #unique = [x for x in unique if x[0] in sources]

        unique = [x for x in unique if x[0] in sources and x not in ['interview_date','interview_age','subject','subjectkey','redcap_event_name']]
        if 'interview_date' in unique:
            print('interview_date' in unique)
        if 'interview_date' not in unique:
            print('interview_date not in unique')
        print(unique)
        self.data.preload(unique)

    def run(self, struct):
        self.transformer.load_map(struct)
        df = self.transformer.transform(self.data, lambda x: x['struct'] == struct)
        df = df[struct]
        df = df.reset_index(drop=True)

        if struct == 'drugscr01':
            renamelist = ['caffeine_s1yn', 'caffeine_s1', 'caffeine_s1pretype', 'caffeine_s1pretime', 'caffeine_s1preday', 'caffeine_s1vsttype1', 'caffeine_s1vsttime1', 'caffeine_s1vsttype2', 'caffeine_s1vsttime2', 'nicotine_s1yn', 'nicotine_s1', 'nicotine_s1pretype', 'nicotine_s1pretime', 'nicotine_s1preday', 'nicotine_s1vsttype1', 'nicotine_s1vsttime1', 'nicotine_s1vsttype2', 'nicotine_s1vsttime2', 'drug1_1', 'drug1_2', 'drug1_3', 'drug1_4', 'drug1_5', 'drug1_6', 'alc_breath1']
            sessions = []
            for i in range(1, 7):
                oldnames = [x.replace('1', str(i), 1) for x in renamelist]
                replacements_dict = dict(zip(oldnames, renamelist))
                session = df[oldnames].rename(columns=replacements_dict)
                session = session.dropna(0, how='all')
                session['version_form'] = "Drug #%s" % i
                sessions.append(session)
            sessions = pd.concat(sessions)

            df = df[['subjectkey', 'src_subject_id', 'interview_date', 'interview_age', 'sex', 'comqother',
                        'alc', 'caffeine_session',
                        'drug', 'nicotine_session']] \
                .merge(sessions, right_index=True, left_index=True)

        self.writer.write(struct, df)
        self.writer.validate(struct)

    def run_all(self):
        pass
