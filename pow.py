# Proof of work
import hashlib


def calculate_hash(data):
    sha = hashlib.sha256()
    sha.update(data.encode('utf-8'))
    return sha.digest()


def validate_hash(hash, difficulty):
    return 0
