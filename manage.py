#!/usr/bin/env python
# -*- coding: UTF-8 -*
import os
from app import create_app, db
from app.main.models import User, Role
from app.english.models import EnglishWord, EnglishMyWord, EnglishMyExercise, EnglishBook, EnglishSetting, EnglishLesson
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ATH_CONFIG') or 'default')
manager = Manager(app)


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


def init_app_data():
    db.drop_all()
    db.create_all()

    Role.insert_roles()
    b1 = EnglishBook(title=u'Side By Side I', description=u'《朗文国际英语教程》第一册', image="images/english/sbs1.png")
    b2 = EnglishBook(title=u'Side By Side II', description=u'《朗文国际英语教程》第二册', image="images/english/sbs2.png")
    b3 = EnglishBook(title=u'Side By Side III', description=u'《朗文国际英语教程》第三册', image="images/english/sbs3.png")
    b4 = EnglishBook(title=u'Side By Side IV', description=u'《朗文国际英语教程》第四册', image="images/english/sbs4.png")
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(b3)
    db.session.add(b4)
    db.session.commit()

    u = User(name='Dad', role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u)
    u2 = User(name='Mum', role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u2)
    u3 = User(name='David', role=Role.query.filter_by(name="Knight").first())
    db.session.add(u3)
    db.session.commit()

    s = EnglishSetting(user_id=u3.id, level1=12, level2=8, level3=3, level4=2)
    db.session.add(s)
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
