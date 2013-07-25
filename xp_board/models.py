import datetime

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
    for key, value in kwargs.iteritems():
        setattr(self, key, value)
    db.session.add(self)
    db.session.commit()
    return self

def create(cls, **kwargs):
    model = cls().update(**kwargs)
    return model


def upsert_by(cls, upsert_key, **kwargs):
    try:
        model, = cls.list_by_column_values(
            [kwargs[upsert_key]],
            column_name=upsert_key
        )
        return model.update(**kwargs)
    except ValueError:
        return cls.create(**kwargs)


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
    def find_user_by_username(cls, username, create_if_missing=False, raise_if_not_found=True):
        try:
            return cls.query.filter(cls.username == username).one()
        except NoResultFound:
            if create_if_missing:
                user = cls(username=username)
                db.session.add(user)
                db.session.commit()
                return user
            if raise_if_not_found:
                raise

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

    # Review functions

    @property
    def pending_primary_reviews(self):
        return self.primary_reviews.filter(ReviewRequest.status == 'pending')

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    # Ticket functions

    @property
    def pending_tickets(self):
        return self.owned_tickets.filter(Ticket.status != 'closed')

    @property
    def closed_tickets(self):
        return self.owned_tickets.filter(Ticket.status == 'closed')

    def tickets_closed_since(self, past_time):
        return self.closed_tickets.filter(Ticket.time_changed > past_time)

    def tickets_closed_in_last(self, time_delta):
        return self.tickets_closed_since(datetime.datetime.now() - time_delta)

    @property
    def tickets_closed_in_last_week(self):
        return self.tickets_closed_in_last(datetime.timedelta(days=7))

    @property
    def pending_and_recently_closed_tickets(self):
        return self.pending_tickets.union(self.tickets_closed_in_last_week)

    @property
    def pending_and_recently_completed_tickets_by_status(self):
        status_to_tickets = {}
        for ticket in self.pending_and_recently_closed_tickets:
            status_to_tickets.setdefault(ticket.completion_status, []).append(ticket)
        return status_to_tickets


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
    def needs_review(self):
        return self.most_recent_review is None or (self.most_recent_review.time_submitted < self.time_last_updated and not self.has_open_issues and not self.has_ship_it)

    @property
    def needs_revision(self):
        return self.has_open_issues or (self.most_recent_review.time_submitted == self.time_last_updated and not self.has_ship_it)

    @property
    def has_open_issues(self):
        return self.code_reviews.filter(
            CodeReview.has_open_issues == True
        ).count() > 0

    @property
    def primary_reviews(self):
        return self.code_reviews.filter(
            CodeReview.reviewer_id == self.primary_reviewer_id
        )

    @property
    def most_recent_review(self):
        try:
            return self.code_reviews.order_by(CodeReview.time_submitted.desc()).limit(1).one()
        except:
            return None

    @property
    def most_recent_primary_review(self):
        try:
            self.primary_reviews.order_by(CodeReview.time_submitted.desc()).limit(1).one()
        except:
            return None

    @property
    def has_ship_it(self):
        return any(code_review.ship_it for code_review in self.code_reviews.all())

    @property
    def has_ship_it_from_primary(self):
        return self.primary_reviews.filter(CodeReview.ship_it == True).count() > 0

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
        backref=orm.backref('primary_reviews', uselist=True, lazy='dynamic'),
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
    has_open_issues = db.Column(db.Boolean)

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
    time_changed = db.Column(db.DateTime)

    @property
    def needs_revision(self):
        return any([
            review_request.needs_revision
            for review_request in self.review_requests
        ])

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
