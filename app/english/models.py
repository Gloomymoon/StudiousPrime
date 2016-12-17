# coding=utf-8
import random
from math import ceil
from flask import current_app
from sqlalchemy import func, distinct, case, sql, and_
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app import db
from utilities import word_mask, word_strong


class EnglishSetting(db.Model):
    __tablename__ = 'english_settings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    total = db.Column(db.Integer, default=25)
    level1 = db.Column(db.Integer, default=25)
    level2 = db.Column(db.Integer, default=0)
    level3 = db.Column(db.Integer, default=0)
    level4 = db.Column(db.Integer, default=0)
    level5 = db.Column(db.Integer, default=0)
    fill_down = db.Column(db.Boolean, default=True)  # allow using lower level word to fill the short of higher level
    fill_level5 = db.Column(db.Boolean, default=True)  # allow using level3 word to fill the total short
    use_mask = db.Column(db.Boolean, default=True)  # allow using word mask in questions
    user = db.relationship('User', back_populates="english_setting", uselist=False)


class EnglishBook(db.Model):
    __tablename__ = 'english_books'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    #words = db.relationship('EnglishWord', back_populates="book", lazy='dynamic')
    mybooks = db.relationship('EnglishMyBook', back_populates="book")
    lessons = db.relationship('EnglishLesson', back_populates="book")

    '''
    def get_lessons(self):
        lessons = db.session.query(EnglishWord.lesson, func.count("*").label("word_count")). \
            filter(EnglishWord.book_id == self.id). \
            group_by(EnglishWord.lesson).order_by(EnglishWord.lesson).all()
        result = []
        for index, row in enumerate(lessons):
            result.append({"lesson": row[0], "count": row[1]})
        return result
    '''


class EnglishMyBook(db.Model):
    __tablename__ = 'english_mybooks'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('english_books.id'), primary_key=True)
    selected = db.Column(db.Boolean, default=False)
    lessons = db.Column(db.String(100), default='')
    add_dt = db.Column(db.DateTime(), default=datetime.utcnow)
    update_dt = db.Column(db.DateTime(), default=datetime.utcnow)
    book = db.relationship('EnglishBook', back_populates="mybooks")
    user = db.relationship('User', back_populates="english_books")

    def word_count(self):
        return sum([len(l.words) for l in self.book.lessons ])

    def add_word(self, word_id):
        if not self.user.english_words.filter(EnglishMyWord.word_id == word_id).one_or_none():
            myword = EnglishMyWord(user_id=self.user_id, word_id=word_id)
            db.session.add(myword)

    def add_words(self):
        """
        When books first added to a user, generate all the MyWords.
        """
        for lesson in self.book.lessons:
            for word in lesson.words:
                self.add_word(word.id)
        db.session.commit()

    '''
    def get_lessons(self):
        l = self.book.lessons.all()
        if len(self.lessons) < len(l):
            self.lessons += '0' * (len(l) - len(self.lessons))
            db.session.commit()
        result = []
        for index, row in enumerate(l):
            result.append({"lesson": row["lesson"], "count": row["count"], "selected": self.lessons[index]})
        return result
    '''

    def get_levels(self):
        levels = db.session.query(EnglishMyWord.level, func.count("*").label("word_count")). \
            join(EnglishMyWord.word).\
            join(EnglishWord.lesson).\
            filter(EnglishLesson.book_id == self.book_id, EnglishMyWord.user_id == self.user_id).\
            group_by(EnglishMyWord.level).order_by(EnglishMyWord.level).all()
        return levels

    def enable_lesson(self, lesson_id):
        lesson = EnglishLesson.query.filter_by(id=lesson_id).one_or_none()
        if lesson:
            if len(self.lessons) < lesson.number:
                self.lessons += '0' * (lesson.number - len(self.lessons))
            self.lessons = self.lessons[:max(0, lesson.number-1)] + '1' + self.lessons[lesson.number:]
            mywords = self.user.english_words.join(EnglishMyWord.word).filter(EnglishWord.lesson_id == lesson_id).all()
            for myword in mywords:
                myword.selected = True
            db.session.commit()
            return True
        return False

    def disable_lesson(self, lesson_id):
        lesson = EnglishLesson.query.filter_by(id=lesson_id).one_or_none()
        if lesson:
            if len(self.lessons) < lesson.number:
                self.lessons += '0' * (lesson.number - len(self.lessons))
            self.lessons = self.lessons[:max(0, lesson.number-1)] + '0' + self.lessons[lesson.number:]
            mywords = self.user.english_words.join(EnglishMyWord.word).filter(EnglishWord.lesson_id == lesson_id).all()
            for myword in mywords:
                myword.selected = False
            db.session.commit()
            return True
        return False

class EnglishLesson(db.Model):
    __tablename__ = 'english_lessons'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('english_books.id'), index=True)
    number = db.Column(db.Integer, index=True)
    title = db.Column(db.String(100))
    book = db.relationship('EnglishBook', back_populates="lessons")
    words = db.relationship('EnglishWord', back_populates="lesson")


class EnglishWord(db.Model):
    __tablename__ = 'english_words'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('english_lessons.id'), index=True)
    english = db.Column(db.String(50), index=True)
    chinese = db.Column(db.String(200))
    example = db.Column(db.String(2000))
    create = db.Column(db.DateTime(), default=datetime.utcnow)
    update = db.Column(db.DateTime(), default=datetime.utcnow)
    mywords = db.relationship('EnglishMyWord', back_populates='word')
    #book = db.relationship('EnglishBook', back_populates="words")
    lesson = db.relationship('EnglishLesson', back_populates="words")


class EnglishMyWord(db.Model):
    __tablename__ = 'english_mywords'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('english_words.id'), primary_key=True)
    selected = db.Column(db.Boolean, default=False)
    tested = db.Column(db.Integer, default=0)
    passed = db.Column(db.Integer, default=0)
    update = db.Column(db.DateTime(), default=datetime.utcnow)
    user = db.relationship("User", back_populates="english_words")
    word = db.relationship("EnglishWord", back_populates="mywords")

    @hybrid_property
    def level(self):
        '''
        单词的等级，根据通过的次数决定
        lvl 1: <=2
            2: <=4
            3: <=6
            4: <=8
            5: >=9
        :return:
        '''
        if self.passed <= 2:
            return 1
        elif self.passed <= 4:
            return 2
        elif self.passed <= 6:
            return 3
        elif self.passed <= 8:
            return 4
        else:
            return 5

    @level.expression
    def level(cls):
        return case([(cls.passed <= 2, 1),
                     (and_(cls.passed > 2, cls.passed <= 4), 2),
                     (and_(cls.passed > 4, cls.passed <= 6), 3),
                     (and_(cls.passed > 6, cls.passed <= 8), 4), ],
                    else_=5)

    def mask(self, seed, use_mask):
        return word_mask(self.word.english, seed=seed, use_mask=use_mask)

    def highlight(self, compare_value):
        return word_strong(self.word.english, compare_value)

    def select(self, selected=True):
        self.selected = selected
        db.session.commit()

    def to_json(self):
        json_myword = {
            'word_id': self.word_id,
            'user_id': self.user_id,
            'book_id': self.word.book_id,
            'book_title': self.word.lesson.book.title,
            'lesson_id': self.word.lesson_id,
            'lesson': self.word.lesson.lesson_title,
            'english': self.word.english,
            'chinese': self.word.chinese,
            'example': self.word.example,
            'tested': self.tested,
            'passed': self.passed,
            'level': self.level,
            'update': self.update
        }
        return json_myword


class EnglishMyExercise(db.Model):
    """
    Question words are stored in self.questions in string format of word.id separated by ','
    EnglishMyExercise() will not generate question words, you should manually call generate_questions() method
    """
    __tablename__ = 'english_myexercises'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total = db.Column(db.Integer, default=0)
    current = db.Column(db.Integer, default=0)
    passed = db.Column(db.Integer, default=0)
    create_dt = db.Column(db.DateTime(), default=datetime.utcnow)
    finish_dt = db.Column(db.DateTime())
    questions = db.Column(db.String(2000))
    questions_level = db.Column(db.String(100))
    questions_result = db.Column(db.String(100))
    questions_answer = db.Column(db.String(5000))
    use_mask = db.Column(db.Boolean)
    user = db.relationship("User", back_populates="english_exercises")

    def has_questions(self):
        if 0 < self.total == len(self.questions.split(',')):
            return True
        return False

    def generate_questions(self):
        # if total > 0 and total equals questions, do nothing
        if not self.has_questions():
            words = []
            total = 0
            self.questions = ''
            numbers = [self.user.english_setting.total,
                       self.user.english_setting.level1,
                       self.user.english_setting.level2,
                       self.user.english_setting.level3,
                       self.user.english_setting.level4,
                       self.user.english_setting.level5,
                       ]
            current_level = 4
            while current_level > 0:
                sample = self.user.random_words(level=current_level, number=numbers[current_level])
                short_number = numbers[current_level]- len(sample)
                words.extend(sample)
                total += len(sample)
                if short_number > 0 and self.user.english_setting.fill_down:
                    if current_level > 1:
                        numbers[current_level - 1] += short_number
                numbers[current_level] = len(sample)
                current_level += -1
            total_short_number = numbers[0] - total - numbers[5]
            if self.user.english_setting.fill_level5 and total_short_number > 0:
                numbers[5] += total_short_number
            sample = self.user.random_words(level=5, number=numbers[5])
            words.extend(sample)
            random.shuffle(words)
            self.total = len(words)
            self.current = 0
            self.passed = 0
            self.create_dt = datetime.utcnow()
            self.questions = ','.join([str(w.word_id) for w in words])
            self.questions_level = ''.join([str(w.level) for w in words])
            self.questions_result = ''
            self.questions_answer = ''
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def get_questions(self):
        questions = []
        answers = self.questions_answer.split(',')

        for index, word_id in enumerate(self.questions.split(',')):
            word = EnglishMyWord.query.filter(
                and_(EnglishMyWord.user_id == self.user_id, EnglishMyWord.word_id == word_id)).first()
            answer = answers[index] if answers[index:] else ''
            result = self.questions_result[index] if self.questions_result[index:] else ''
            level = self.questions_level[index] if self.questions_level[index:] else ''
            questions.append({"index": index, "word": word, "level":level, "answer": answer, "result": result})
        return questions

    def get_question_by_index(self, index):
        try:
            answers = self.questions_answer.split(',')
            word = EnglishMyWord.query.filter(
                and_(EnglishMyWord.user_id == self.user_id, EnglishMyWord.word_id == self.questions.split(',')[index])).first()
            answer = answers[index] if answers[index:] else ''
            result = self.questions_result[index] if self.questions_result[index:] else ''
            level = self.questions_level[index] if self.questions_level[index:] else ''
            return {"index": index, "word": word, "level": level, "answer": answer, "result": result}
        except:
            return None

    def get_errors(self, level=0):
        errors = []
        if not self.questions is None:
            for index, word_id in enumerate(self.questions.split(',')):
                result = self.questions_result[index] if self.questions_result[index:] else ''
                question_level = self.questions_level[index] if self.questions_level[index:] else ''
                if result != '1' and (level == 0 or level == question_level):
                    errors.append(word_id)
        return errors

'''
class Statistic():
    @staticmethod
    def wrong_words(user_id, number):
        wq = db.session.query(EnglishQuestion.word_id.label('word_id'), func.count(EnglishQuestion.index).label('count'))\
            .join(EnglishQuestion.exercise)\
            .filter(EnglishExercise.user_id==user_id)\
            .filter(EnglishQuestion.result < 1).group_by(EnglishQuestion.word_id)\
            .filter(EnglishExercise.finish > '1800-01-01')\
            .order_by(func.count(EnglishQuestion.index).desc()).limit(number).all()
        w = Word.query.filter(Word.id.in_((x.word_id for x in wq))).all()
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
        aws = db.session.query(MyWord.level.label("level"), func.count(MyWord.word_id).label('count')) \
            .filter(MyWord.user_id == user_id) \
            .group_by(MyWord.level).order_by(MyWord.level.asc()).all()
        aws2 = db.session.query(func.count(MyWord.word_id).label('TotalWords')).filter(
            MyWord.user_id == user_id).first()
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
'''


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
