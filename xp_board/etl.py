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

    def post_transform(self):
        pass

    def load(self):
        return self.loader.load(self.transformed)


class MultipleExtractETL(ETL):

    @classmethod
    def execute(cls, identifiers):
        for data in cls.extractor.extract(identifiers):
            yield cls(data).execute_transform_load()

    @classmethod
    def execute_one(cls, identifiers):
        extracted = cls.extractor.extract(identifiers)
        return cls(extracted).execute_transform_load()

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.transformed = {}

    def execute_transform_load(self):
        self.transform()
        self.post_transform()
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

    def __init__(self, model_class, upsert_key='id', model_column_name=None):
        self.model_class = model_class
        self.transformed_upsert_key = upsert_key
        self.model_column_upsert_key = model_column_name or self.transformed_upsert_key

    def load(self, transformed):
        models = self.model_class.list_by_column_values(
            [transformed[self.transformed_upsert_key]],
            column_name=self.model_column_upsert_key
        )
        if not models: return self.model_class(**transformed)

        model, = models
        for attribute_name, value in transformed.iteritems():
            setattr(model, attribute_name, value)
        return model

