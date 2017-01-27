from random import sample
from flask import jsonify, current_app, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.english.models import EnglishMyExercise, EnglishMyWord, EnglishSummary, EnglishMyBook, EnglishLesson,\
    EnglishWord
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
                               'and total > 0 '
                               'group by date(create_dt) ')
    rows = []
    for r in result:
        rows.append({
            'date': r['date'].strftime("%Y-%m-%d"),
            'accuracy': "%.2f" % r['accuracy']
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


@api.route('/e/lesson/enable/<int:lesson_id>')
@login_required
def enable_lesson(lesson_id):
    lesson = EnglishLesson.query.filter_by(id=lesson_id).one_or_none()
    if lesson:
        mybook = current_user.english_books.filter(EnglishMyBook.book_id == lesson.book_id).one_or_none()
        if mybook:
            if mybook.enable_lesson(lesson_id):
                return jsonify({"lesson": lesson_id, "result": 'true'})
    return jsonify({"lesson": lesson_id, "result": 'false'})


@api.route('/e/lesson/disable/<int:lesson_id>')
@login_required
def disable_lesson(lesson_id):
    lesson = EnglishLesson.query.filter_by(id=lesson_id).one_or_none()
    if lesson:
        mybook = current_user.english_books.filter(EnglishMyBook.book_id == lesson.book_id).one_or_none()
        if mybook:
            if mybook.disable_lesson(lesson_id):
                return jsonify({"lesson": lesson_id, "result": 'true'})
    return jsonify({"lesson": lesson_id, "result": 'false'})


@api.route('/e/recognition/check/', methods=['POST'])
@login_required
def recognition_checks():
    word_id = request.values.get('word_id', 0)
    answer = request.values.get('answer', '')
    type = request.values.get('english_question', 0)
    current = request.values.get('current', '-1')
    recognition = current_user.english_recognition
    word = EnglishWord.query.filter_by(id=word_id).first()
    if current and int(current) != recognition.current:
        return jsonify({}), 500
    if type:
        correct_answer = word.chinese
    else:
        correct_answer = word.english
    if word and answer == correct_answer:
        result = "true"
        recognition.passed += 1
    else:
        result = "false"
    recognition.current += 1
    db.session.add(recognition)
    db.session.commit()
    return jsonify({"answer": correct_answer, "result": result, "raw_answer": answer})
