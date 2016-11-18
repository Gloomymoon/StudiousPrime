from random import sample
from flask import jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.englicise.models import EnglishExercise, EnglishWordScore, EnglishSummary
from . import api


@api.route('/e/word/next')
@login_required
def next_new_word():
    ws = EnglishWordScore.random_word(current_user.id, 1)
    return jsonify(ws.to_json())


@api.route('/e/exercise/summary')
@login_required
def get_exercise_summary():
    result = db.engine.execute()



@api.route('/e/exercise/vintage')
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
                               'from english_wordscores '
                               'where user_id=' + str(current_user.id))
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
