# 🔐 Secure Chat

A Flask-based messaging application that encrypts every message using **ephemeral X25519 key exchange, HKDF-SHA256 key derivation, and ChaCha20-Poly1305 authenticated encryption**. Messages are view-once and automatically expire after one hour.

Built as a hands-on project to explore applied cryptography, secure key handling, and ephemeral messaging design.

## ✨ Features

- **Per-message ephemeral keys:** Generates a new ephemeral X25519 key pair for every message.
- **Authenticated encryption:** Uses ChaCha20-Poly1305 (AEAD) to provide confidentiality and integrity. Tampered ciphertext fails authentication.
- **Secure key derivation:** Derives encryption keys from the X25519 shared secret using HKDF-SHA256 with a context label.
- **Random nonces:** Generates a unique 96-bit nonce for each message using `os.urandom`.
- **Self-destructing messages:**
  - **View-once:** Messages are deleted after the recipient reads them.
  - **Time-based expiry:** Messages older than one hour are purged.
- **Privacy-focused UI:** Sent messages display as `(sent securely)`, and messages intended for other users are not shown.
- **User registration:** Automatically generates an X25519 key pair for each user.

## 🧠 How It Works

The application uses an ephemeral Elliptic Curve Diffie–Hellman (ECDH) exchange to derive a symmetric encryption key for each message.

### Encryption and Decryption Flow

```text
Sender                                              Receiver
------                                              --------
1. Look up receiver's static X25519 public key
2. Generate ephemeral X25519 key pair
   (eph_priv, eph_pub)
3. shared_secret = X25519(eph_priv, receiver_pub)
4. key = HKDF-SHA256(shared_secret, info="secure-chat")
5. Encrypt plaintext using ChaCha20-Poly1305
6. Store {ciphertext, nonce, eph_pub}  ----------->  7. Retrieve message
                                                      8. shared_secret =
                                                         X25519(receiver_priv, eph_pub)
                                                      9. key = HKDF-SHA256(
                                                         shared_secret,
                                                         info="secure-chat")
                                                     10. Decrypt ciphertext
                                                     11. Mark as read and
                                                         delete the message
```

### Message Lifecycle

1. The sender retrieves the recipient's public key.
2. A fresh ephemeral X25519 key pair is generated.
3. Both parties derive the same shared secret through ECDH.
4. HKDF-SHA256 derives a symmetric encryption key.
5. ChaCha20-Poly1305 encrypts the message.
6. The database stores the ciphertext, nonce, and ephemeral public key.
7. The recipient derives the decryption key and decrypts the message.
8. The message is deleted after being read, subject to the application's cleanup logic.

**Storage:** The message table stores ciphertext, nonce, and the ephemeral public key rather than plaintext. However, because private keys are stored server-side and the server performs decryption, this implementation is not true end-to-end encryption.

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| ORM | Flask-SQLAlchemy |
| Database | SQLite |
| Cryptography | Python `cryptography` library |
| Key Exchange | X25519 |
| Key Derivation | HKDF-SHA256 |
| Authenticated Encryption | ChaCha20-Poly1305 |
| Frontend | HTML, CSS, Jinja2 templates |

## 📁 Project Structure

```text
secure-chat/
├── app.py                 # Flask routes and application logic
├── crypto_utils.py        # Key generation and encryption/decryption helpers
├── models.py              # SQLAlchemy models for users and messages
├── templates/
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   └── chat.html          # Messaging interface
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── LICENSE                # MIT License
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- Git

### 1. Clone the Repository

Replace `<your-username>` with your GitHub username.

```bash
git clone https://github.com/<your-username>/secure-chat.git
cd secure-chat
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open the Application

Navigate to:

```text
http://127.0.0.1:5000
```

Register two users and use separate browsers or an incognito window to test messaging between them.

The SQLite database is created automatically on the first run, assuming the application initializes its database as configured.

## 📦 Dependencies

The `requirements.txt` file contains:

```text
Flask
Flask-SQLAlchemy
cryptography
```

## ⚠️ Security Notes and Known Limitations

This is an **educational project, not a production-ready messaging application**. The following limitations are important to understand.

| Limitation | Details |
|---|---|
| No true end-to-end encryption | Private keys are stored server-side, and the server decrypts messages for display. A compromised server may expose private keys and message contents. |
| No password authentication | Login is username-based, without passwords or multi-factor authentication. |
| Unencrypted private keys at rest | Private keys are stored as raw bytes in SQLite. |
| Hardcoded Flask secret key | The application secret should be supplied through environment-based configuration. |
| Debug mode | Flask debug mode must be disabled in production. |
| No CSRF protection | Forms are not protected against Cross-Site Request Forgery. |
| No rate limiting | The application lacks throttling against brute-force attempts and abuse. |
| Unsigned messages | Ed25519 helpers exist in `crypto_utils.py` but are not yet integrated into the message flow. Sender identity is therefore not cryptographically authenticated. |
| No replay protection | The message counter is currently a placeholder. |
| Cleanup depends on application logic | Time-based expiry may not be enforced continuously if cleanup runs only when pages are loaded. |

**Important:** Ephemeral sender keys alone do not guarantee complete forward secrecy. The recipient's long-term private key is used to derive the message key, so compromise of that private key may expose previously stored messages if their ciphertext and ephemeral public keys are available.

## 🗺 Roadmap

- [ ] Add password authentication with Argon2id or bcrypt password hashing.
- [ ] Implement true end-to-end encryption using client-side key generation and storage with Web Crypto or libsodium.js.
- [ ] Integrate Ed25519 digital signatures and verify signatures when messages are received.
- [ ] Implement message counters and sequence numbers for replay protection.
- [ ] Encrypt private keys at rest using a password-derived key or a key management service (KMS).
- [ ] Add CSRF protection and rate limiting.
- [ ] Configure secure session cookies using `HttpOnly`, `Secure`, and `SameSite` attributes.
- [ ] Move secrets into environment variables and disable debug mode.
- [ ] Deploy through a production WSGI server.
- [ ] Implement a background job for reliable message expiration and cleanup.

## 📚 What I Learned

- Designing an ECDH + HKDF + AEAD encryption pipeline.
- Understanding how ephemeral keys work and what security guarantees they provide.
- Distinguishing server-side encryption from genuine end-to-end encryption.
- Applying authenticated encryption to protect message confidentiality and integrity.
- Understanding secure key storage, message lifecycle management, and cryptographic identity verification.
- Performing threat modeling and documenting security limitations honestly.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
