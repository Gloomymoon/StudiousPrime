import random
from flask import current_app
from sqlalchemy import func, distinct, case, sql
from datetime import datetime
from app import db
from utilities import word_mask, word_strong


class EnglishSetting(db.Model):
    __tablename__ = 'english_settings'
    category = db.Column(db.String(64), primary_key=True)
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(64))


class EnglishBookWords(db.Model):
    __tablename__ = 'english_bookwords'
    word_id = db.Column(db.Integer, db.ForeignKey('english_words.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('english_books.id'), primary_key=True)
    lesson = db.Column(db.Integer, default=0)


class EnglishBook(db.Model):
    __tablename__ = 'english_books'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))
    words = db.relationship('EnglishBookWords',
                            foreign_keys=[EnglishBookWords.book_id],
                            backref=db.backref('books', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')


class EnglishWord(db.Model):
    __tablename__ = 'english_words'
    id = db.Column(db.Integer, primary_key=True)
    #book_id = db.Column(db.Integer, db.ForeignKey('english_books.id'), index=True)
    english = db.Column(db.String(64), index=True)
    chinese = db.Column(db.String(200))
    example = db.Column(db.String(2000))
    create = db.Column(db.DateTime(), default=datetime.utcnow)
    update = db.Column(db.DateTime(), default=datetime.utcnow)
    questions = db.relationship('EnglishQuestion', backref=db.backref('word', lazy='joined'), lazy='dynamic')
    scores = db.relationship('EnglishWordScore', backref=db.backref('word', lazy='joined'), lazy='dynamic')
    books = db.relationship('EnglishBookWords',
                            foreign_keys=[EnglishBookWords.word_id],
                            backref=db.backref('words', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')


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
        elif value <= 8:
            target.level = 4
        else:
            target.level = 5

    @staticmethod
    def random_word(user_id, level):
        q = EnglishWordScore.query.filter_by(user_id=user_id)
        ws = None
        level = level
        while not ws and level <= 5:
            ws = random.sample(q.filter_by(level=level).all(), 1)[0]
            level += 1
        return ws

    def to_json(self):
        json_wordscore = {
            'word_id': self.word_id,
            'user_id': self.user_id,
            'english': self.word.english,
            'chinese': self.word.chinese,
            'example': self.word.example,
            'score': self.score,
            'level': self.level,
            'update': self.update
        }
        return json_wordscore


class EnglishQuestion(db.Model):
    __tablename__ = 'english_questions'
    index = db.Column(db.Integer, primary_key=True)
    exc_id = db.Column(db.Integer, db.ForeignKey('english_exercises.id'), index=True, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('english_words.id'))
    english = db.Column(db.String(64))
    level = db.Column(db.Integer, default=0)
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
            w = EnglishWordScore.query.filter_by(user_id=self.user_id).filter_by(word_id=q['word_id']).first()
            question = EnglishQuestion(index=index, exc_id=self.id, word_id=q['word_id'], english=w.word.english, word_mask=word_mask(w.word.english), level=w.level)
            db.session.add(question)
        db.session.commit()
        result = EnglishQuestion.query.filter_by(exc_id=self.id).all()
        self.total = len(result)
        db.session.add(self)
        db.session.commit()
        return self.total


db.event.listen(EnglishWordScore.score, 'set', EnglishWordScore.on_changed_score)


class EnglishStatistic():
    @staticmethod
    def wrong_words(user_id, number):
        wq = db.session.query(EnglishQuestion.word_id.label('word_id'), func.count(EnglishQuestion.index).label('count'))\
            .join(EnglishQuestion.exercise)\
            .filter(EnglishExercise.user_id==user_id)\
            .filter(EnglishQuestion.result < 1).group_by(EnglishQuestion.word_id)\
            .filter(EnglishExercise.finish > '1800-01-01')\
            .order_by(func.count(EnglishQuestion.index).desc()).limit(number).all()
        w = EnglishWord.query.filter(EnglishWord.id.in_((x.word_id for x in wq))).all()
        return w

    @staticmethod
    def achievements(user_id):
        val1 = sql.expression.literal_column("1.0")
        ae = db.session.query(func.count(EnglishExercise.id).label('TotalExercises'),
                              func.sum(EnglishExercise.total).label('TotalQuestions'),
                              func.sum(EnglishExercise.correct).label('TotalCorrects'),
                              func.sum(case([(EnglishExercise.correct == EnglishExercise.total, 1)], else_=0)).label(
                                  'TotalFullScore'),
                              func.max(EnglishExercise.finish).label('LastFinish'),
                              func.max((EnglishExercise.correct * val1 / EnglishExercise.total)).label('HighestCorrect'),
                              ) \
            .filter(EnglishExercise.user_id == user_id) \
            .filter(EnglishExercise.finish > '1800-01-01').first()
        aq = db.session.query(func.count(distinct(EnglishQuestion.word_id)).label('TotalTestWords'),
                              ).join(EnglishQuestion.exercise).filter(EnglishExercise.user_id == user_id) \
            .filter(EnglishExercise.finish > '1800-01-01').first()
        aq2 = db.session.query(func.count(distinct(EnglishQuestion.word_id)).label('TotalCorrectWords')
                               ).join(EnglishQuestion.exercise) \
            .filter(EnglishExercise.user_id == user_id) \
            .filter(EnglishExercise.finish > '1800-01-01') \
            .filter(EnglishQuestion.result > 0).first()
        aq3 = db.session.query(EnglishQuestion.english, func.count(EnglishQuestion.index).label('count')) \
            .join(EnglishQuestion.exercise) \
            .filter(EnglishExercise.user_id == user_id) \
            .filter(EnglishQuestion.result < 1).group_by(EnglishQuestion.english) \
            .filter(EnglishExercise.finish > '1800-01-01') \
            .order_by(func.count(EnglishQuestion.index).desc()).limit(5).all()
        aws = db.session.query(EnglishWordScore.level.label("level"), func.count(EnglishWordScore.word_id).label('count')) \
            .filter(EnglishWordScore.user_id == user_id) \
            .group_by(EnglishWordScore.level).order_by(EnglishWordScore.level.asc()).all()
        aws2 = db.session.query(func.count(EnglishWordScore.word_id).label('TotalWords')).filter(
            EnglishWordScore.user_id == user_id).first()
        achievements = {'TotalExercises': ae.TotalExercises,
                        'TotalQuestions': ae.TotalQuestions,
                        'TotalCorrects': ae.TotalCorrects,
                        'TotalFullScore': ae.TotalFullScore,
                        'LastFinish': ae.LastFinish,
                        'HighestCorrect': ae.HighestCorrect,
                        'TotalTestWords': aq.TotalTestWords,
                        'TotalCorrectWords': aq2.TotalCorrectWords,
                        'WrongWords': aq3,
                        'WordScores': aws,
                        'TotalWords': aws2.TotalWords
                        }
        return achievements


class EnglishSummary(db.Model):
    __tablename__ = 'english_summary'
    user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    total = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    count = db.Column(db.Integer)

    def to_json(self):
        json_summary = {
            'user_id': self.user_id,
            'date': self.date,
            'total': self.total,
            'correct': self.correct,
            'duration': self.duration,
            'count': self.count,
            'accuracy': "%2.1f" % (self.correct / self.total * 100),
        }
        return json_summary
