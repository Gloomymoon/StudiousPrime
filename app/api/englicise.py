from random import sample
from flask import jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.englicise.models import EnglishExercise, EnglishWordScore
from . import api


@api.route('/e/word/next')
@login_required
def next_new_word():
    ws = EnglishWordScore.random_word(current_user.id, 1)
    return jsonify(ws.to_json())