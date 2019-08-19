from hashlib import sha256
def encoding(password):
    string = str(sha256(password.encode("utf-8")).hexdigest())
    return string