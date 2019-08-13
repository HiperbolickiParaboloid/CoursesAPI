from hashlib import sha256
def encoding(password):
    string = str(sha256(password.encode()).hexdigest())
    return string