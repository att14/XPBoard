import re

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

from . import app


db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(length=20), unique=True)

    @classmethod
    def find_user_by_username(cls, username, create_if_not_found=False):
        try:
            return cls.query.filter(cls.username == username).one()
        except NoResultFound:
            if create_if_not_found:
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
    db.Column('is_primary', db.Boolean)
)


class ReviewRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    submitter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(length=512))

    submitter = db.relationship(
        User,
        backref=db.orm.backref('submitted_reviews', use_list=True),
        use_list=False,
        lazy='dynamic'
    )

    primary_reviewer = db.relationship(
        User,
        primary_join=(
            'and_(ReviewRequest.id == ReviewRequestToReviewer.review_request_id,'
            'ReviewRequestToReviewere.is_primary)'
        ),
        use_list=False
    )

    reviewers = db.relationship(
        User,
        primary_join='ReviewRequest.id == ReviewRequestToReviewer.review_request_id',
        backref='code_reviews'
    )


class CodeReview(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    review_request_id =  db.Column(db.Integer, db.ForeignKey(ReviewRequest.id))

    review_request = db.relationship(
        ReviewRequest,
        backref=db.orm.backref('code_reviews', use_list=True),
        use_list=False
    )


class Ticket(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    status = db.Column(db.String(length=32))

    owner = db.relationship(
        User,
        primaryjoin='Ticket.owner_id == User.id',
        backref='owned_tickets',
        use_list=False
    )
    reporter = db.relationship(
        User,
        primaryjoin='Ticket.reporter_id == User.id',
        backref='reported_tickets',
        use_list=False
    )