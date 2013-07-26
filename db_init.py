from xp_board import models


models.db.drop_all()
models.db.create_all()
