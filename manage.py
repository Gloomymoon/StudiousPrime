#!/usr/bin/env python
# -*- coding: UTF-8 -*
import os, sys
import csv
from app import create_app, db
from app.main.models import User, Role
from app.english.models import EnglishWord, EnglishMyWord, EnglishMyExercise, EnglishBook, EnglishSetting, EnglishLesson
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ATH_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Word=EnglishWord, MyWord=EnglishMyWord,
                MyExercise=EnglishMyExercise, Book=EnglishBook, Setting=EnglishSetting)


manager.add_command("runserver", Server(host="0.0.0.0", port=(os.environ.get('PORT') or 5000)))
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()



def add_book(title, description="", image="images/english/default.png"):
    b = EnglishBook.query.filter(EnglishBook.title == title).first()
    if not b:
        b = EnglishBook(title=title, description=description, image=image)
        db.session.add(b)
        db.session.commit()
        print "Book [" + title + "] added."


def import_words(filename):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    basedir = sys.path[0]
    if os.path.isfile(basedir):
        basedir = os.path.dirname(basedir)
    basedir = os.path.join(basedir, "app/static/doc")
    b = None
    if os.path.isfile(os.path.join(basedir, filename)):
        with open(os.path.join(basedir, filename), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for line in reader:
                print line
                if len(line) < 6:
                    line.append('')
                if not b or b.title != line[0]:
                    b = EnglishBook.query.filter(EnglishBook.title==line[0]).first()
                if not b:
                    print "Can not find book [" + line[0] + "], please add book first."
                    exit()
                    # b = EnglishBook(title=line[0], description=line[0])
                    # db.session.add(b)
                    # db.session.commit()
                l = EnglishLesson.query.filter(EnglishLesson.book_id == b.id, EnglishLesson.title == line[2]).first()
                if not l:
                    l = EnglishLesson(title=line[2], number=line[1], book_id=b.id)
                    db.session.add(l)
                    db.session.commit()
                w = EnglishWord.query.filter(EnglishWord.lesson_id == l.id, EnglishWord.english == line[3]).first()
                if not w:
                    w = EnglishWord(english=line[3], chinese=unicode(line[4]), example=line[5],
                                    lesson_id=l.id)
                    db.session.add(w)
                    db.session.commit()
                    print line[0], line[1], line[2], line[3], line[4], " Add"


def init_app_data():
    db.drop_all()
    db.create_all()

    Role.insert_roles()

    u = User(name='Gloomymoon', password="111111", role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u)
    u2 = User(name='Haoer', password="111111", role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u2)
    u3 = User(name='David', password="111111", role=Role.query.filter_by(name="Knight").first())
    db.session.add(u3)
    db.session.commit()

    s = EnglishSetting(user_id=u3.id, level1=12, level2=8, level3=3, level4=2)
    db.session.add(s)
    db.session.commit()

    add_book("Oxford 3A", "Oxford 3A")
    import_words("Oxford3A.csv")
    add_book("WTE 3A", "Longman Welcome to English 3A")
    import_words("WTE3A.csv")

    '''
    b1 = EnglishBook(title=u'Side By Side I', description=u'《朗文国际英语教程》第一册', image="images/english/sbs1.png")
    b2 = EnglishBook(title=u'Side By Side II', description=u'《朗文国际英语教程》第二册', image="images/english/sbs2.png")
    b3 = EnglishBook(title=u'Side By Side III', description=u'《朗文国际英语教程》第三册', image="images/english/sbs3.png")
    b4 = EnglishBook(title=u'Side By Side IV', description=u'《朗文国际英语教程》第四册', image="images/english/sbs4.png")
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(b3)
    db.session.add(b4)
    db.session.commit()

    l1 = []
    l2 = []
    l3 = []
    l4 = []
    for i in range(10):
        l1.append(EnglishLesson(number=i + 1, book_id=b1.id, title='M1L' + str(i + 1)))
        l2.append(EnglishLesson(number=i + 1, book_id=b2.id, title='M2L' + str(i + 1)))
        l3.append(EnglishLesson(number=i + 1, book_id=b3.id, title='M3L' + str(i + 1)))
        l4.append(EnglishLesson(number=i + 1, book_id=b4.id, title='M4L' + str(i + 1)))
        db.session.add(l1[i])
        db.session.add(l2[i])
        db.session.add(l3[i])
        db.session.add(l4[i])
        db.session.commit()

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 1), example='Test Example',
                        lesson_id=l1[i/5].id)
        db.session.add(w)
        db.session.commit()
    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 51), example='Test Example',
                        lesson_id=l2[i/5].id)
        db.session.add(w)
        db.session.commit()

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 101), example='Test Example',
                        lesson_id=l3[i/5].id)
        db.session.add(w)
        db.session.commit()

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 151), example='Test Example',
                        lesson_id=l4[i/5].id)
        db.session.add(w)
        db.session.commit()
    '''


def add_new_book():
    add_book("3E", u"3E口语二级")
    import_words("3E.csv")
