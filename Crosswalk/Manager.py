class Manager:
    def __init__(self, data=None, writer=None, transformer=None):
        self.data = data
        self.writer = writer
        self.transformer = transformer

    def preload_data(self):
        unique = self.transformer.get_unique_variables()
        self.data.preload(unique)

    def run(self, struct):
        self.transformer.load_map(struct)
        df = self.transformer.transform(self.data, lambda x: x['struct'] == struct)
        df = df[struct]
        self.writer.write(struct, df)
        self.writer.validate(struct)

    def run_all(self):
        pass
