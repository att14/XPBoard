from . import models


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
        self.post_transform()
        return self.load()

    def extract(self):
        self.raw_data = self.extractor.extract(self.identifier)
        return self.raw_data

    def transform(self):
        self.transformed.update(
            dict(
                (key, self.apply_transformer(key, transformer))
                for key, transformer in self.transformers.iteritems()
            )
        )

    def apply_transformer(self, key, transformer):
        if not transformer:
            return self.raw_data[key]
        if isinstance(transformer, str):
            return self.raw_data[transformer]
        return transformer.transform(self.raw_data)

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


class ModelLoader(Loader):

    def __init__(self, model_class, upsert_key='id', model_column_name=None):
        self.model_class = model_class
        self.transformed_upsert_key = upsert_key
        self.model_column_upsert_key = model_column_name or self.transformed_upsert_key

    def load(self, transformed):
        model_instances = self.model_class.list_by_column_values(
            [transformed[self.transformed_upsert_key]],
            column_name=self.model_column_upsert_key
        )
        if not model_instances:
            model = self.model_class(**transformed)
        else:
            model, = model_instances
            for attribute_name, value in transformed.iteritems():
                setattr(model, attribute_name, value)

        models.db.session.add(model)
        models.db.session.commit()
        return model


class FieldTransform(Transformer):

    def __init__(self, field_name):
        self.field_name = field_name

    def transform(self, item_resource):
        return self._transform(item_resource.fields)

    def _transform(self, fields):
        return fields[self.field_name]
