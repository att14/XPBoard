from . import etl
from . import reviewboard_client
from . import models


class UserExtractor(etl.Extractor):

    def extract(self, username):
        return reviewboard_client.client.get_user_info(username).next()


class UserETL(etl.MultipleExtractETL):

    extractor = UserExtractor()

    transformers = {
        'username': etl.FieldTransform('username'),
        'first_name': etl.FieldTransform('first_name'),
        'last_name': etl.FieldTransform('last_name')
    }

    loader = etl.ModelLoader(models.User, upsert_key='username')

    @classmethod
    def execute_one(cls, username):
        try:
            return models.User.maybe_find_user_by_username(username) or \
                super(UserETL, cls).execute_one(username)
        except reviewboard_client.UserNotFoundError:
            models.User.find_user_by_username(username, create_if_missing=True)