from random import sample
from flask import jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.english.models import EnglishMyExercise, EnglishMyWord, EnglishSummary, EnglishMyBook
from . import api


@api.route('/e/word/next')
@login_required
def next_new_word():
    w = current_user.random_words(1, 1)[0]
    return jsonify(w.to_json())


@api.route('/e/exercise/vintage')
@login_required
def get_exercise_summary():
    result = db.engine.execute('select date(create_dt) as date, avg(passed*100.0/total) as accuracy '
                               'from english_myexercises '
                               'where user_id=' + str(current_user.id) + ' '
                               'and current >= total '
                               'group by date(create_dt) ')
    rows = []
    for r in result:
        rows.append({
            'date': r['date'],
            'accuracy': r['accuracy']
        })
    return jsonify({
        'date': [r['date'] for r in rows],
        'accuracy': [r['accuracy'] for r in rows]
    })


@api.route('/e/exercise/vintage2')
@login_required
def get_exercise_vintage():
    summary = EnglishSummary.query.filter_by(user_id=current_user.id).order_by(EnglishSummary.date.asc()).all()
    return jsonify({'total': [s.total for s in summary],
                    'date': [s.date.isoformat() for s in summary],
                    'accuracy': ["%2.2f" % (s.correct * 100.0 / s.total) for s in summary],
                    'count': len(summary)
                    })


@api.route('/e/word/level')
@login_required
def get_word_level():
    result = db.engine.execute('select level, count(*) as count '
                               'from english_mywords '
                               'where user_id=' + str(current_user.id) + ' '
                               'group by level')
    rows = []
    for r in result:
        rows.append({
            'level': r['level'],
            'count': r['count']
        })
    return jsonify({
        'level': [r['level'] for r in rows],
        'count': [r['count'] for r in rows]
    })


@api.route('/e/book/enable/<int:book_id>/<int:lesson_id>')
@login_required
def enable_lesson(book_id, lesson_id):
    mybook = current_user.english_books.filter(EnglishMyBook.book_id == book_id).one_or_none()
    if mybook:
        if mybook.enable_lesson(lesson_id):
            return jsonify({"lesson": lesson_id, "result": 'true'})
    return jsonify({"lesson": lesson_id, "result": 'false'})


@api.route('/e/book/disable/<int:book_id>/<int:lesson_id>')
@login_required
def disable_lesson(book_id, lesson_id):
    mybook = current_user.english_books.filter(EnglishMyBook.book_id == book_id).one_or_none()
    if mybook:
        if mybook.disable_lesson(lesson_id):
            return jsonify({"lesson": lesson_id, "result": 'true'})
    return jsonify({"lesson": lesson_id, "result": 'false'})