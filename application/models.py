from application.database import db
import os

class USER(db.Model):
    __tablename__ = "USER"
    USER_ID = db.Column(db.Integer, autoincrement = True, primary_key = True)
    USER_NAME = db.Column(db.String, nullable = False, unique = True)
    PASSWORD = db.Column(db.String, nullable = False)
    FOLLOWER_COUNT = db.Column(db.Integer, nullable =False)
    POST_COUNT = db.Column(db.Integer, nullable=False)


class POST(db.Model):
    __tablename__ ="POST"
    POST_ID = db.Column(db.Integer, autoincrement = True, primary_key = True)
    POST_TITLE = db.Column(db.Integer, nullable = False)
    POST_CONTENT = db.Column(db.TEXT)
    POST_LIKES = db.Column(db.Integer, nullable = False)
    POST_DISLIKES = db.Column(db.Integer, nullable=False)
    AUTHOR = db.relationship("USER", secondary="POST_USER")
    ENGAGEMENT = db.relationship("USER", secondary = "LIKE_DISLIKE")

class POST_USER(db.Model):
    __tablename__ = "POST_USER"
    POST_ID = db.Column(db.Integer, db.ForeignKey("POST.POST_ID"), primary_key = True, unique=True)
    USER_ID = db.Column(db.Integer, db.ForeignKey("USER.USER_ID"), primary_key = True)

class COMMENTS(db.Model):
    __tablename__ = "COMMENTS"
    COMMENT_ID = db.Column(db.Integer, primary_key = True)
    COMMENT_CONTENT = db.Column (db.String)
    POST_ID = db.Column(db.Integer, db.ForeignKey("POST.POST_ID"), nullable = False)
    USER_NAME = db.Column(db.Integer, db.ForeignKey("USER.USER_NAME"), nullable = False)

class FOLLOWER_FOLLOWING(db.Model):
    __tablename__ = "FOLLOWER_FOLLOWING"
    FOLLOWER_ID = db.Column(db.Integer, db.ForeignKey("USER.USER_ID"), primary_key=True)
    FOLLOWED_ID = db.Column(db.Integer, db.ForeignKey("USER.USER_ID"), primary_key=True)

class LIKE_DISLIKE(db.Model):
    __tablename__ = "LIKE_DISLIKE"
    POST_ID = db.Column(db.Integer, db.ForeignKey("POST.POST_ID"), primary_key = True)
    USER_ID = db.Column(db.Integer, db.ForeignKey("USER.USER_ID"), primary_key = True)
    LIKE_DISLIKE = db.Column(db.Integer, nullable = False)

class sqlite_sequence(db.Model):
    __tablename__ = "sqlite_sequence"
    name = db.Column(db.String, primary_key=True)
    seq = db.Column(db.Integer)