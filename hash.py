from hashlib import md5

def hash_passwd(pwd):
    return md5(pwd.encode('utf-8')).hexdigest()

def check_passwd(entered, h):
    return hash_passwd(entered) == h
