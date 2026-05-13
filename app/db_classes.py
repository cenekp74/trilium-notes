from app import db, login_manager
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin

def _now():
    return datetime.now(timezone.utc)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(60), nullable=False)