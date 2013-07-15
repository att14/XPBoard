from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import orm

from . import app
from . import lib


def list_by_column_values(cls, column_values, column_name='id'):
    return cls.query.filter(getattr(cls, column_name).in_(column_values)).all()


def list_by_ids(cls, ids):
    return cls.query.filter(cls.id.in_(ids)).all()


def find_by_id(cls, model_id):
    model_list = cls.list_by_ids([model_id])
    return model_list[0] if model_list else None



db = SQLAlchemy(app)
db.Model.list_by_column_values = classmethod(list_by_column_values)
db.Model.list_by_ids = classmethod(list_by_ids)
db.Model.find_by_id = classmethod(find_by_id)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(length=20))
    last_name = db.Column(db.String(length=20))

    username = db.Column(db.String(length=20), unique=True)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @classmethod
    def search_for_user(cls, user_string, suggestions=None):
        try:
            return cls.find_user_by_username(user_string)
        except NoResultFound:
            pass

        if suggestions:
            return min(
            	suggestions,
            	key=lambda user: user.levenshtein_on_names(user_string)
            )
        return None

    @classmethod
    def find_user_by_username(cls, username, create_if_missing=False):
        try:
            return cls.query.filter(cls.username == username).one()
        except NoResultFound:
            if create_if_missing:
                user = cls(username=username)
                db.session.add(user)
                db.session.commit()
                return user
            raise

    def levenshtein_on_names(self, string):
        if not all([self.first_name, self.last_name, self.username]):
            import ipdb; ipdb.set_trace()
        best_match = min(
            [self.first_name, self.last_name, self.username, self.full_name],
            key=lambda name: lib.levenshtein(name.lower(), string.lower())
        )
        return lib.levenshtein(best_match, string)


ReviewRequestToReviewer = db.Table(
    'review_request_to_reviewer',
    db.Model.metadata,
    db.Column('review_request_id', db.Integer, db.ForeignKey("review_request.id")),
    db.Column('reviewer_id', db.Integer, db.ForeignKey("user.id")),
)


class ReviewRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    submitter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    primary_reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(length=512))
    summary = db.Column(db.String(length=128))

    submitter = db.relationship(
        User,
        primaryjoin='ReviewRequest.submitter_id == User.id',
        backref=orm.backref('submitted_reviews', uselist=True),
        uselist=False,
    )

    primary_reviewer = db.relationship(
        User,
        primaryjoin='ReviewRequest.primary_reviewer_id == User.id',
        backref=orm.backref('primary_reviews', uselist=True),
        uselist=False,
    )

    reviewers = db.relationship(
        User,
        secondary=ReviewRequestToReviewer,
        backref='review_requests'
    )


class CodeReview(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reviewer_id = db.Column(db.Integer, db.ForeignKey(User.id))
    review_request_id = db.Column(db.Integer, db.ForeignKey(ReviewRequest.id))
    ship_it = db.Column(db.Boolean)

    review_request = db.relationship(
        ReviewRequest,
        backref=orm.backref('code_reviews', uselist=True),
        uselist=False
    )
    reviewer = db.relationship(
        User,
        backref=orm.backref('code_reviews', uselist=True),
        uselist=False
    )


class Ticket(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    status = db.Column(db.String(length=32))

    owner = db.relationship(
        User,
        primaryjoin='Ticket.owner_id == User.id',
        backref=orm.backref('owned_tickets', uselist=True),
        uselist=False
    )
    reporter = db.relationship(
        User,
        primaryjoin='Ticket.reporter_id == User.id',
        backref='reported_tickets',
        uselist=False
    )
