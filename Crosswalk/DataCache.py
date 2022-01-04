from collections import defaultdict
import time

class DataCache:
    def __init__(self, *sources):
        self.sources = {}
        self.add_source(*sources)
        self.df = {}
        self.DF = {}

    def add_source(self, *sources):
        for source in sources:
            self.sources[source.get_source_name()] = source

    def preload(self, fields):
        d = defaultdict(set)
        for source, field in fields:
            d[source].add(field)

        for source, fields in d.items():
            if source not in self.sources:
                print(f'The source "{source}" is used in the maps, but not defined in DataCache. Skipping preload.')
                continue
            start = time.time()
            df, DF = self.sources[source].load(list(fields))
            self.df[source] = df
            self.DF[source] = DF
            print("Timing: ", source, (time.time()-start))

    def get(self, source, field):
        if field in self.df[source]:
            return (
                self.df[source][field].copy(),
                self.DF[source][field].copy()
            )
        else:
            raise Exception('Field not in source', source, field)

    def get_fields(self, source, names):
        data = []
        for name in names:
            data.extend(self.get(source, name))

        return data
