#!/usr/bin/env python
# -*- coding: UTF-8 -*
import os
from app import create_app, db
from app.main.models import User, Role
from app.english.models import EnglishWord, EnglishMyWord, EnglishMyExercise, EnglishBook, EnglishSetting
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ATH_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Word=EnglishWord, MyWord=EnglishMyWord,
                MyExercise=EnglishMyExercise, Book=EnglishBook, Setting=EnglishSetting)


manager.add_command("runserver", Server(host="0.0.0.0", port=5000))
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
    b1 = EnglishBook(title=u'Side By Side I', description=u'《朗文国际英语教程》第一册', image="images/english/sbs1.jpg")
    b2 = EnglishBook(title=u'Side By Side II', description=u'《朗文国际英语教程》第二册', image="images/english/sbs2.jpg")
    b3 = EnglishBook(title=u'Side By Side III', description=u'《朗文国际英语教程》第三册', image="images/english/sbs3.jpg")
    b4 = EnglishBook(title=u'Side By Side IV', description=u'《朗文国际英语教程》第四册', image="images/english/sbs4.jpg")
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

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 1), example='Test Example', book_id=b1.id,
                        lesson=i / 10 + 1)
        db.session.add(w)
        db.session.commit()
    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 51), example='Test Example', book_id=b2.id,
                        lesson=i / 10 + 1)
        db.session.add(w)
        db.session.commit()

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 101), example='Test Example', book_id=b3.id,
                        lesson=i / 10 + 1)
        db.session.add(w)
        db.session.commit()

    for i in range(50):
        w = EnglishWord(english='test', chinese=u'测试中文' + str(i + 151), example='Test Example', book_id=b4.id,
                        lesson=i / 10 + 1)
        db.session.add(w)
        db.session.commit()
