from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chatbot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    personality = db.Column(db.String(200))
    template = db.Column(db.String(50))
    config_file = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InteractionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('chatbot.id'), nullable=False)
    user_message = db.Column(db.String(500))
    bot_response = db.Column(db.String(500))
    intent = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
