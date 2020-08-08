import hashlib
import os

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (salt + key)

def check_password(entered, storedHash):
    salt = storedHash[:32]
    key = storedHash[32:]
    newKey = hashlib.pbkdf2_hmac('sha256', entered.encode('utf-8'), salt, 100000)
    if key == newKey:
        return True
    else:
        return False
