from flask import Flask, render_template, request, redirect, session
from models import db, User, Message
from datetime import datetime, timedelta
from crypto_utils import *
from cryptography.hazmat.primitives import serialization
import base64
import os

# ✅ DEBUG DB PATH
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

print("USING DB:", db_path)

# ✅ CREATE APP
app = Flask(__name__)
app.secret_key = "supersecret"

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
db.init_app(app)

with app.app_context():
    db.create_all()

# ✅ HOME
@app.route("/")
def home():
    return redirect("/login")

# ✅ LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]

        user = User.query.filter_by(username=username).first()

        if user:
            session["username"] = username
            return redirect("/chat")
        else:
            return render_template("login.html", error="User not found")

    return render_template("login.html")

# ✅ REGISTER (FIXED → X25519)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="Username already exists")

        private_key, public_key = generate_x25519_keys()

        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

        user = User(
            username=username,
            public_key=public_bytes,
            private_key=private_bytes
        )

        db.session.add(user)
        db.session.commit()

        session["username"] = username

        return redirect("/chat")

    return render_template("register.html")

# ✅ CHAT (ENCRYPT + DECRYPT)
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    # Load private key
    user = User.query.filter_by(username=username).first()
    user_private_key = load_x25519_private_key(user.private_key)

    # 🔐 SEND MESSAGE
    if request.method == "POST":
        sender = username
        receiver = request.form["receiver"]
        message = request.form["message"]

        receiver_user = User.query.filter_by(username=receiver).first()
        if not receiver_user:
            return "Receiver not found"

        receiver_public_key = load_x25519_public_key(receiver_user.public_key)

        eph_private, eph_public = generate_x25519_keys()
        shared_key = derive_shared_key(eph_private, receiver_public_key)

        ciphertext, nonce = encrypt_message(shared_key, message)

        msg = Message(
            sender=sender,
            receiver=receiver,
            ciphertext=ciphertext,
            nonce=nonce,
            signature=b"",
            counter=1,
            ephemeral_public_key=serialize_public_key(eph_public)
        )

        db.session.add(msg)
        db.session.commit()

    # 🔐 RECEIVE + SELF-DESTRUCT LOGIC
    messages = Message.query.all()
    decrypted_messages = []

    for msg in messages:
        try:
            # 🔥 DELETE AFTER 1 HOUR
            if datetime.utcnow() - msg.timestamp > timedelta(hours=1):
                db.session.delete(msg)
                db.session.commit()
                continue

            if msg.receiver == username:

                # 🔥 DELETE AFTER VIEW ONCE
                if msg.is_read:
                    db.session.delete(msg)
                    db.session.commit()
                    continue

                eph_pub = load_x25519_public_key(msg.ephemeral_public_key)
                shared_key = derive_shared_key(user_private_key, eph_pub)
                plaintext = decrypt_message(shared_key, msg.ciphertext, msg.nonce)

                decrypted_messages.append(f"{msg.sender} → {plaintext}")

                # 🔥 MARK AS READ
                msg.is_read = True
                db.session.commit()

            elif msg.sender == username:
                decrypted_messages.append(f"You → (sent securely)")

            else:
                decrypted_messages.append("(not for you)")

        except Exception:
            decrypted_messages.append("⚠️ Cannot decrypt")

    return render_template("chat.html", messages=decrypted_messages)

# ✅ RUN
if __name__ == "__main__":
    app.run(debug=True)