class ETL(object):

    # `extractor` is an object that knows how to fetch data to be
    # transformed from a single argument.
    extractor = None

    # `transformer` is an object with a `transform` method that operates on the value
    # returned by the extractor.
    transformer = None

    # `loader` is an object with a `load` metheod that operates on the output of the
    # transform phase.
    loader = None

    def __init__(self, identifier):
        self.identifier = identifier
        self.raw_data = None
        self.transformed = None
        self.loaded = None

    def execute_transform_load(self):
        self.transform()
        return self.load()

    def check_existing_value(self):
        return None

    def execute(self, force=False):
        self.extract()
        return (not force and self.check_existing_value()) or self.execute_transform_load()

    def extract(self):
        self.raw_data = self.extractor.extract(self.identifier)
        return self.raw_data

    def transform(self):
        self.transformed = self.transformer.transform(self.raw_data)
        return self.transformed

    def load(self):
        self.loaded = self.loader.load(self.transformed)
        return self.loaded


class MultipleExtractETL(ETL):

    @classmethod
    def check_for_existing_value(cls):
        return None

    @classmethod
    def execute(cls, identifier):
        for data in cls.extractor.extract(identifier):
            yield cls.check_for_existing_value(data) or cls(data).execute_transform_load()

    @classmethod
    def execute_one(cls, identifier):
        extracted, = cls.extractor.extract(identifier)
        return cls(extracted).execute_transform_load()

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.transformed = None
        self.loaded = None


class NoOpExtractor(object):

    @classmethod
    def extract(self, obj):
        return obj


class ModelLoader(object):

    def __init__(self, model_class, upsert_key='id'):
        self.model_class = model_class
        self.upsert_key = upsert_key

    def load(self, transformed):
        return self.model_class.upsert_by(self.upsert_key)(**transformed)


class SubTransformTransformer(object):

    def __init__(self, transformers):
        self.transformers = transformers

    def transform(self, raw_data):
        transformed = {}
        for transformer in self.transformers:
            transformer.transform(raw_data, transformed)
        return transformed


class SingleKeySubTransform(object):

    def __init__(self, output_key='', **kwargs):
        self.output_key = output_key

    def transform(self, raw_data, transformed):
        transformed[self.output_key] = self.get_value(raw_data, transformed)
        return transformed


class ItemGetterTransform(SingleKeySubTransform):

    def __init__(self, input_key='', **kwargs):
        self.input_key = input_key
        kwargs.setdefault('output_key', input_key)
        super(ItemGetterTransform, self).__init__(**kwargs)

    def get_value(self, raw_data, _):
        return raw_data[self.input_key]


class SimpleFieldTransform(ItemGetterTransform):

    def get_value(self, item_resource, _):
        return item_resource.fields[self.input_key]


class FieldTransform(SingleKeySubTransform):

    def transform(self, item_resource, transformed):
        transformed[self.output_key] = self.get_value(
            item_resource.fields,
            transformed
        )