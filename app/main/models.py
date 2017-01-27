import random
import operator
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from app.english.models import EnglishMyWord


class Permission:
    VIEW = 0x01
    PRACTISE = 0x02
    MANAGE = 0x04   # Add books and change exercise settings
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', back_populates='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Youngling': (Permission.VIEW, False),
            'Padawan': (Permission.VIEW | Permission.PRACTISE, True),
            'Knight': (Permission.VIEW | Permission.PRACTISE | Permission.MANAGE, False),
            'Master': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.id


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(200), index=True, default="")
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    since = db.Column(db.DateTime(), default=datetime.utcnow)
    role = db.relationship("Role", back_populates="users")

    english_books = db.relationship('EnglishMyBook', back_populates='user', cascade="all, delete, delete-orphan", lazy="dynamic")
    english_words = db.relationship('EnglishMyWord', back_populates='user', cascade="all, delete, delete-orphan", lazy="dynamic")
    english_exercises = db.relationship('EnglishMyExercise', back_populates='user', cascade="all, delete, delete-orphan", lazy="dynamic")
    english_setting = db.relationship('EnglishSetting', back_populates='user', cascade="all, delete, delete-orphan", uselist=False)
    english_recognition = db.relationship('EnglishRecognition', back_populates='user', cascade="all, delete, delete-orphan", uselist=False)

    '''
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.name == 'admin':
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    '''

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if not self.password_hash:
            return True
        if not password:
            return False
        return check_password_hash(self.password_hash, password)

    def verify_user(self):
        return self.confirmed

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self, project='admin'):
        return self.can(Permission.ADMINISTER)

    def ping(self, ip):
        self.last_seen = datetime.utcnow()

    def __repr__(self):
        return '<User %r %r>' % (self.id, self.name)

    def random_words(self, level=0, number=1, selected=True):
        if 1 <= level <= 5:
            words = [word for word in self.english_words if word.level == level and (selected is not True or word.selected is True)]
        else:
            words = [word for word in self.english_words if selected is not True or word.selected is True]
        if words and number < len(words):
            return random.sample(words, number)
        else:
            return words

    def error_words(self, level=0, number=1):
        errors = []
        for exercise in self.english_exercises:
            errors.extend(exercise.get_errors(level=level))
        errors_count = {e: errors.count(e) for e in set(errors)}
        errors_result = sorted(errors_count.items(), key=operator.itemgetter(0))[:number]
        if len([x[0] for x in errors_result if x[0] > 0]) > 0:
            words = EnglishMyWord.query.filter_by(user_id = self.id)\
                .filter(EnglishMyWord.word_id.in_([x[0] for x in errors_result if x[0] > 0])).order_by(EnglishMyWord.tested.desc()).all()
            return words
        else:
            return []

    def random_recognition_words(self, seed=0, number=4, selected=True):
        random.seed(seed)
        result_words = self.random_words(1, selected)
        other_words = []
        if len(result_words) and result_words[0]:
            other_words = [word for word in self.english_words if word.word_id != result_words[0].word_id and word.word.lesson_id == result_words[0].word.lesson_id]
            if len(other_words) < number - 1:
                other_words = [word for word in self.english_words if word.word_id != result_words[0].word_id and word.word.lesson.book_id == result_words[0].word.lesson.book_id]
            if len(other_words) < number - 1:
                other_words = [word for word in self.english_words if
                       word.word_id != result_words[0].word_id]
            if len(other_words) > number - 1:
                other_words = random.sample(other_words, number - 1)
        result_words.extend(other_words)
        return result_words

    def has_unfinished_exercise(self):
        for exercise in self.english_exercises:
            if exercise.current < exercise.total:
                return exercise
        return None


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
