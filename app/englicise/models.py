import random
from flask import current_app
from datetime import datetime
from app import db
from utilities import word_mask, word_strong


class EnglishBook(db.Model):
    __tablename__ = 'english_books'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))
    words = db.relationship('EnglishWord', backref=db.backref('book', lazy='joined'), lazy='dynamic')


class EnglishWord(db.Model):
    __tablename__ = 'english_words'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('english_books.id'), index=True)
    english = db.Column(db.String(64), index=True)
    chinese = db.Column(db.String(200))
    example = db.Column(db.String(2000))
    create = db.Column(db.DateTime(), default=datetime.utcnow)
    update = db.Column(db.DateTime(), default=datetime.utcnow)
    questions = db.relationship('EnglishQuestion', backref=db.backref('word', lazy='joined'), lazy='dynamic')


class EnglishWordScore(db.Model):
    __tablename__ = 'english_wordscores'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('english_words.id'), primary_key=True)
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, index=True, default=1)
    update = db.Column(db.DateTime(), default=datetime.utcnow)

    @staticmethod
    def on_changed_score(target, value, oldvalue, initiator):
        if value <= 2:
            target.level = 1
        elif value <= 4:
            target.level = 2
        elif value <= 6:
            target.level = 3
        elif value <= 9:
            target.level = 4
        else:
            target.level = 5


class EnglishQuestion(db.Model):
    __tablename__ = 'english_questions'
    index = db.Column(db.Integer, primary_key=True)
    exc_id = db.Column(db.Integer, db.ForeignKey('english_exercises.id'), index=True, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('english_words.id'))
    english = db.Column(db.String(64))
    word_mask = db.Column(db.String(200))
    answer = db.Column(db.String(64))
    result = db.Column(db.Integer)

    @property
    def answer_highlight(self):
        return word_strong(self.answer, self.english)


class EnglishExercise(db.Model):
    __tablename__ = 'english_exercises'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total = db.Column(db.Integer)
    current = db.Column(db.Integer, default=0)
    correct = db.Column(db.Integer, default=0)
    start = db.Column(db.DateTime(), default=datetime.utcnow)
    finish = db.Column(db.DateTime())
    questions = db.relationship('EnglishQuestion', backref=db.backref('exercise', lazy='joined'), lazy='dynamic')

    def generate_questions(self):
        if self.current == 0:
            EnglishQuestion.query.filter_by(exc_id=self.id).delete()
            db.session.commit()
        words = EnglishWordScore.query.filter_by(user_id=self.user_id)
        questions = []
        question_numbers = current_app.config["QUESTIONS_PER_LEVEL"]
        current_level = 4
        if words:
            while current_level > 0:
                sample_words = words.filter_by(level=current_level).all()
                sample_num = min(len(sample_words), question_numbers[current_level])
                sub_words = random.sample(sample_words, sample_num)
                for word in sub_words:
                    questions.append({"word_id": word.word_id, "order": random.random()})
                question_numbers[current_level-1] += question_numbers[current_level] - len(sub_words)
                current_level += -1
        questions.sort(key=lambda obj:obj.get('order'))
        for index, q in enumerate(questions):
            w = EnglishWord.query.filter_by(id=q['word_id']).first()
            question = EnglishQuestion(index=index, exc_id=self.id, word_id=q['word_id'], english=w.english, word_mask=word_mask(w.english))
            db.session.add(question)
            db.session.add(self)
        db.session.commit()
        result = EnglishQuestion.query.filter_by(exc_id=self.id).all()
        self.total = len(result)
        db.session.commit()
        return self.total


db.event.listen(EnglishWordScore.score, 'set', EnglishWordScore.on_changed_score)
