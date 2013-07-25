import logging

from . import etl
from . import reviewboard_client
from . import models


class UserExtractor(object):

    @classmethod
    def extract(self, username):
        return reviewboard_client.client.get_user_info(username).next()


UserTransformer = etl.SubTransformTransformer([
    etl.SimpleFieldTransform(input_key='username'),
    etl.SimpleFieldTransform(input_key='first_name'),
    etl.SimpleFieldTransform(input_key='last_name'),
])


UserLoader = etl.ModelLoader(models.User, upsert_key='username')


class UserETL(etl.ETL):

    extractor = UserExtractor
    transformer = UserTransformer
    loader = UserLoader

    def maybe_execute(self):
        return self.check_for_existing_value() or self.execute()

    def check_for_existing_value(self):
        return models.User.find_user_by_username(
            self.identifier,
            raise_if_not_found=False
        )

    def execute(self):
        try:
            return super(UserETL, self).execute()
        except reviewboard_client.UserNotFoundError:
            logging.warning(
                ("Unable to find user {0} in reviewboard. "
                 "Creating user anyway").format(self.identifier)
            )
            return models.User.find_user_by_username(
                self.identifier,
                create_if_missing=True
            )


class UserETLByUserInfo(etl.ETL):

    extractor = etl.NoOpExtractor
    transformer = UserTransformer
    loader = UserLoader