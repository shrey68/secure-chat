from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    public_key = db.Column(db.LargeBinary)
    private_key = db.Column(db.LargeBinary)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50))
    receiver = db.Column(db.String(50))
    ciphertext = db.Column(db.LargeBinary)
    nonce = db.Column(db.LargeBinary)
    signature = db.Column(db.LargeBinary)
    counter = db.Column(db.Integer)
    ephemeral_public_key = db.Column(db.LargeBinary)

    # 🔥 NEW FIELDS
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)