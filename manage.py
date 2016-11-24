#!/usr/bin/env python
# -*- coding: UTF-8 -*
import os
from app import create_app, db
from app.main.models import User, Role
from app.englicise.models import EnglishWord, EnglishWordScore, EnglishExercise, \
    EnglishQuestion, EnglishBook, EnglishSetting
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ATH_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                EnglishWord=EnglishWord, EnglishWordScore=EnglishWordScore,
                EnglishExercise=EnglishExercise, EnglishQuestion=EnglishQuestion, EnglishBook=EnglishBook)

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
    b = EnglishBook(name='Default')
    db.session.add(b)
    u = User(name='Dad', role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u)
    u2 = User(name='Mum', role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u2)
    u3 = User(name='David', role=Role.query.filter_by(permissions=0x01).first())
    db.session.add(u3)
    db.session.commit()
    '''
    for i in range(50):
        w = EnglishWord(english='Test'+str(i+1), chinese='Test'+str(i+1))
        db.session.add(w)
        db.session.commit()
        ws = EnglishWordScore(word_id=w.id, user_id=u3.id, score=i/5)
        db.session.add(ws)
        db.session.commit()
    '''


def add_wordscores():
    wsQuery = EnglishWordScore.query.filter_by(user_id=3)
    for w in EnglishWord.query.all():
        ws = wsQuery.filter_by(word_id=w.id).first()
        if not ws:
            ws = EnglishWordScore(word_id=w.id, user_id=3)
            db.session.add(ws)
            db.session.commit()

def add_settings():
    db.create_all()
    s = EnglishSetting(category='level', user_id=3, key='total', value='25')
    s1 = EnglishSetting(category='level', user_id=3, key='1', value='12')
    s2 = EnglishSetting(category='level', user_id=3, key='2', value='8')
    s3 = EnglishSetting(category='level', user_id=3, key='3', value='3')
    s4 = EnglishSetting(category='level', user_id=3, key='4', value='2')
    s5 = EnglishSetting(category='level', user_id=3, key='5', value='0')
    db.session.add(s)
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)
    db.session.add(s4)
    db.session.add(s5)
    db.session.commit()