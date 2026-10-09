🔐 Secure Chat
A Flask-based messaging app that encrypts every message with a fresh ephemeral X25519 key exchange, HKDF-SHA256 key derivation, and ChaCha20-Poly1305 authenticated encryption. Messages are view-once and auto-expire after 1 hour.

Built as a hands-on project to explore applied cryptography, secure key handling, and ephemeral messaging design.

✨ Features
Per-message forward secrecy (sender side): a new ephemeral X25519 key pair is generated for every message
Authenticated encryption: ChaCha20-Poly1305 (AEAD) guarantees confidentiality and integrity; tampered ciphertext fails to decrypt
Key derivation: ECDH shared secret is passed through HKDF-SHA256 with a context label before use
Random 96-bit nonce per message from os.urandom
Self-destructing messages:
View-once: a message is deleted after the recipient reads it
Time-based expiry: anything older than 1 hour is purged
Privacy in the UI: sent messages display as (sent securely); messages for other users are never shown
Simple registration/login flow with automatic key-pair generation per user
🧠 How It Works
Sender                                              Receiver
------                                              --------
1. Look up receiver's static X25519 public key
2. Generate ephemeral X25519 key pair (eph_priv, eph_pub)
3. shared_secret = X25519(eph_priv, receiver_pub)
4. key = HKDF-SHA256(shared_secret, info="secure-chat")
5. ciphertext, nonce = ChaCha20-Poly1305(key, plaintext)
6. Store { ciphertext, nonce, eph_pub }  ───────────▶  7. shared_secret = X25519(receiver_priv, eph_pub)
                                                       8. key = HKDF-SHA256(shared_secret, info="secure-chat")
                                                       9. plaintext = ChaCha20-Poly1305-Decrypt(key, ciphertext, nonce)
                                                      10. Mark as read → deleted on next load
Only ciphertext, nonce, and the ephemeral public key are stored in the message table — no plaintext is persisted.

🛠 Tech Stack
Layer	Technology
Backend	Python 3, Flask, Flask-SQLAlchemy
Database	SQLite
Cryptography	cryptography library (X25519, HKDF, ChaCha20-Poly1305)
Frontend	HTML / CSS (Jinja2 templates)
📁 Project Structure
secure-chat/
├── app.py             # Flask routes: register, login, chat, self-destruct logic
├── crypto_utils.py    # Key generation, ECDH, HKDF, AEAD encrypt/decrypt helpers
├── models.py          # SQLAlchemy models: User, Message
├── templates/
│   ├── login.html
│   ├── register.html
│   └── chat.html
├── requirements.txt
└── README.md
🚀 Getting Started
bash
# 1. Clone
git clone https://github.com/<your-username>/secure-chat.git
cd secure-chat

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
Open http://127.0.0.1:5000, register two users (use two different browsers or an incognito window), and start chatting. The SQLite database is created automatically on first run.

requirements.txt

Flask
Flask-SQLAlchemy
cryptography
⚠️ Security Notes & Known Limitations
This is an educational project, not a production messenger. Being explicit about its limits:

Limitation	Detail
Not true end-to-end encryption	User private keys are stored server-side, and the server decrypts messages for display. A compromised server or database exposes keys.
No password authentication	Login is by username only; there are no passwords or MFA.
Private keys at rest are unencrypted	Keys are stored as raw bytes in SQLite.
Hardcoded Flask secret_key and debug=True	Must be replaced with an environment-provided secret and debug disabled for any deployment.
No CSRF protection / rate limiting	Forms are not CSRF-protected; no brute-force or abuse throttling.
Unsigned messages	Sender identity is not cryptographically authenticated (Ed25519 helpers exist in crypto_utils.py but are not yet wired in), so sender spoofing is possible at the application layer.
No replay protection	The counter field is a placeholder.
🗺 Roadmap
 Password authentication with Argon2id/bcrypt hashing
 Move to true E2EE: generate keys client-side (Web Crypto / libsodium.js), keep private keys on the device only
 Sign every message with Ed25519 and verify on receipt
 Message counters / sequence numbers for replay protection
 Encrypt private keys at rest (password-derived key or KMS)
 CSRF tokens, rate limiting, secure session cookies (HttpOnly, Secure, SameSite)
 Environment-based configuration and a production WSGI server
 Background job for message expiry instead of cleanup on page load
📚 What I Learned
Designing an ECDH + HKDF + AEAD pipeline and why each step exists
Why ephemeral keys matter and what they do (and don't) protect against
The difference between transport/server-side encryption and genuine end-to-end encryption
Threat modeling a small app and documenting its weaknesses honestly

📄 License
MIT — see LICENSE.

