from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import orm

from . import app


db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(length=20), unique=True)

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
        backref='code_reviews'
    )



class CodeReview(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    review_request_id =  db.Column(db.Integer, db.ForeignKey(ReviewRequest.id))

    review_request = db.relationship(
        ReviewRequest,
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