import os
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import x25519

# 🔐 Load X25519 private key
def load_x25519_private_key(data):
    return x25519.X25519PrivateKey.from_private_bytes(data)

# 🔐 Load X25519 public key
def load_x25519_public_key(data):
    return x25519.X25519PublicKey.from_public_bytes(data)

# 🔐 Serialize public key
def serialize_public_key(pub_key):
    return pub_key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw
    )


# Generate Ed25519 keys
def generate_ed25519_keys():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# Generate Ephemeral X25519 keys
def generate_x25519_keys():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# Derive shared session key
def derive_shared_key(private_key, peer_public_key):
    shared_secret = private_key.exchange(peer_public_key)

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'secure-chat',
        backend=default_backend()
    )
    return hkdf.derive(shared_secret)

# Encrypt message
def encrypt_message(key, plaintext):
    nonce = os.urandom(12)
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext.encode(), None)
    return ciphertext, nonce

# Decrypt message
def decrypt_message(key, ciphertext, nonce):
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, ciphertext, None).decode()

# Sign message
def sign_message(private_key, message):
    return private_key.sign(message)

# Verify signature
def verify_signature(public_key, message, signature):
    public_key.verify(signature, message)