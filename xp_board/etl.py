class Extractor(object):

    def extract(self, identifier):
        raise NotImplemented()


class Transformer(object):

    def transform(self, raw_data):
        raise NotImplemented()


class Loader(object):

    def load(self, transformed):
        raise NotImplemented()


class ETL(object):

    # `extractor` should be an object that knows how to fetch data to be
    # transformed from a single argument.
    extractor = None

    # `transformers` should be a dictionary of transformation objects that should be
    # applied to extracted data.
    transformers = None

    # `loader` should be a loader instance. It should operate on a dictionary of
    # transformed values

    def __init__(self, identifier):
        self.identifier = identifier
        self.raw_data = None
        self.transformed = {}

    def execute(self):
        self.extract()
        self.transform()
        return self.load()

    def extract(self):
        self.raw_data = self.extractor.extract(self.identifier)
        return self.raw_data

    def transform(self):
        self.transformed.update(
            dict(
                (key, transformer.transform(self.raw_data))
                for key, transformer in self.transformers.iteritems()
            )
        )

    def load(self):
        return self.loader.load(self.transformed)


class MultipleExtractETL(ETL):

    @classmethod
    def execute(cls, identifiers):
        for data in cls.extractor.extract(identifiers):
            yield cls(data).execute_transform_load()

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.transformed = {}

    def execute_transform_load(self):
        self.transform()
        return self.load()

    def transform(self):
        self.transformed.update(
            dict(
                (key, transformer.transform(self.raw_data))
                for key, transformer in self.transformers.iteritems()
            )
        )

    def load(self):
        return self.loader.load(self.transformed)


class ModelLoader(Loader):

    def __init__(self, model_class, upsert_key='id'):
        self.model_class = model_class
        self.upsert_key = upsert_key

    def load(self, transformed):
        model = self.model_class.find_by_id(transformed[self.upsert_key])
        if not model: return self.model_class(**transformed)

        for attribute_name, value in transformed.iteritems():
            setattr(model, attribute_name, value)
        return model

