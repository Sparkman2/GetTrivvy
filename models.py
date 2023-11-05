from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_packs = db.relationship('TriviaPack', backref='creator', lazy=True)
    scores = db.relationship('Scoreboard', backref='user', lazy=True)
    liked_packs = db.relationship('Like', backref='user', lazy='dynamic')

    def calculate_score_from_likes(self):
        # Sum the likes from all packs created by this user
        return db.session.query(db.func.count(Like.id)).join(TriviaPack).filter(
            TriviaPack.creator_id == self.id).scalar()


    # Most of these function are to ensure that once user is logged in
    # They new post button will appear
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_active(self):
        return self.active

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


class TriviaPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Ensure that the foreign key reference uses the correct table name.
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # The backref here will create a virtual column in Question, and it can be anything. It doesn't have to match the table name.
    questions = db.relationship('Question', backref='triviapack', lazy=True)
    likes = db.relationship('Like', backref='triviapack', lazy='dynamic')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    incorrect_answers = db.Column(db.String(800), nullable=False)
    pack_id = db.Column(db.Integer, db.ForeignKey('trivia_pack.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pack_id = db.Column(db.Integer, db.ForeignKey('trivia_pack.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Like user_id: {}, pack_id: {}>'.format(self.user_id, self.pack_id)



class Scoreboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)





