from app import db
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref


@login.user_loader
def load_user(id):
    return User.query.get(int(id))



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    position = db.Column(db.String(500))
    users = db.relationship('TemporaryUser', backref='room', lazy='dynamic')
    allowed_users = db.Column(db.String(500))

    def __repr__(self):
        return "Room {}, pos: {}".format(self.id, self.position)


class TemporaryUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'TU: origin name is {}'.format(self.user.username)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    temp = db.relationship('TemporaryUser', backref='user', lazy='dynamic')
    is_admin = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

