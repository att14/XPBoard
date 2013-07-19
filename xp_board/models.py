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


def update(self, **kwargs):
    if type(self) == CodeReview:
        import ipdb; ipdb.set_trace()
        print
    for key, value in kwargs.iteritems():
        setattr(self, key, value)
    return self

def create(cls, **kwargs):
    model = cls().update(**kwargs)
    db.session.add(model)
    db.session.commit()
    return model


def upsert_by(cls, upsert_key):
    def upsert(**kwargs):
        try:
            model, = cls.list_by_column_values(
                [kwargs[upsert_key]],
                column_name=upsert_key
            )
            return model.update(**kwargs)
        except ValueError:
            return cls.create(**kwargs)
    return upsert


db = SQLAlchemy(app)
db.Model.list_by_column_values = classmethod(list_by_column_values)
db.Model.list_by_ids = classmethod(list_by_ids)
db.Model.find_by_id = classmethod(find_by_id)
db.Model.create = classmethod(create)
db.Model.upsert_by = classmethod(upsert_by)
db.Model.update = update



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(length=20))
    last_name = db.Column(db.String(length=20))

    username = db.Column(db.String(length=20), unique=True)

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
    def maybe_find_user_by_username(cls, *args, **kwargs):
        try:
            return cls.find_user_by_username(*args, **kwargs)
        except NoResultFound:
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

    @property
    def pending_primary_reviews(self):
        return filter(
            lambda review_request: review_request.ship_it_status == 'pending',
            self.primary_reviews
        )

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def pending_tickets_by_status(self):
        pending_tickets = self.owned_tickets.filter(Ticket.status != 'closed').all()
        status_to_tickets = {}
        for ticket in pending_tickets:
            status_to_tickets.setdefault(ticket.completion_status, []).append(ticket)

        return status_to_tickets

    def levenshtein_on_names(self, string):
        if not string:
            return 1000
        names = filter(
            lambda name: name is not None,
            [self.first_name, self.last_name, self.username, self.full_name]
        )
        best_match = min(
            names,
            key=lambda name: lib.levenshtein(name.lower(), string.lower())
        )
        return lib.levenshtein(best_match, string)


ReviewRequestToReviewer = db.Table(
    'review_request_to_reviewer',
    db.Model.metadata,
    db.Column('review_request_id', db.Integer, db.ForeignKey("review_request.id")),
    db.Column('reviewer_id', db.Integer, db.ForeignKey("user.id")),
)


ReviewRequestToTicket = db.Table(
    'review_request_to_ticket',
    db.Model.metadata,
    db.Column('review_request_id', db.Integer, db.ForeignKey("review_request.id")),
    db.Column('ticket_id', db.Integer, db.ForeignKey("ticket.id")),
)


class ReviewRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    submitter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    primary_reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(length=512))
    summary = db.Column(db.String(length=128))
    status = db.Column(db.String(length=20))

    time_last_updated = db.Column(db.DateTime)

    @property
    def has_ship_it(self):
        return any(code_review.ship_it for code_review in self.code_reviews.all())

    @property
    def has_ship_it_from_primary(self):
        return self.code_reviews.filter(
            CodeReview.reviewer_id == self.primary_reviewer_id
        ).filter(
            CodeReview.ship_it == True
        ).count() > 0

    @property
    def ship_it_status(self):
        if self.status == 'submitted':
            return self.status

        if self.has_ship_it_from_primary:
            return 'ship_it'

        return self.status

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

    time_submitted = db.Column(db.DateTime)

    review_request = db.relationship(
        ReviewRequest,
        backref=orm.backref('code_reviews', uselist=True, lazy='dynamic'),
        uselist=False
    )
    reviewer = db.relationship(
        User,
        backref=orm.backref('code_reviews', uselist=True, lazy='dynamic'),
        uselist=False
    )


class Ticket(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    status = db.Column(db.String(length=32))
    resolution = db.Column(db.String(length=32))
    summary = db.Column(db.String(length=256))
    component = db.Column(db.String(length=64))
    priority = db.Column(db.Integer)

    @property
    def completion_status(self):
        if self.status == 'closed':
            return self.status

        if self.review_requests:
            # TODO: do something better here
            review_request = self.review_requests[0]
            if review_request.ship_it_status != 'pending':
                return review_request.ship_it_status
            return 'in_review'

        return self.status

    owner = db.relationship(
        User,
        primaryjoin='Ticket.owner_id == User.id',
        backref=orm.backref('owned_tickets', uselist=True, lazy='dynamic'),
        uselist=False
    )

    reporter = db.relationship(
        User,
        primaryjoin='Ticket.reporter_id == User.id',
        backref='reported_tickets',
        uselist=False
    )

    review_requests = db.relationship(
        ReviewRequest,
        secondary=ReviewRequestToTicket,
        backref='tickets'
    )
