from werkzeug.security import safe_str_cmp
from Teachers import mycol_teachers
from hashlib import sha256

class User():
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password
    def __str__(self):
        return f'username: {self.username}, password: {self.password}, _id: {self.id}'


br = 1
users = [ User(1, "admin", str(sha256("admin".encode("utf-8")).hexdigest()))
]

def authenticate(username, password):
    teachers = list(mycol_teachers.find())
    for i in teachers:
        user = User((len(users)+1), i.get("username",""), i.get("password",""))
        users.append(user)
    for i in users:
        print (i)
    username_mapping = {u.username: u for u in users}
    user = username_mapping.get(username, None)
    print(user)
    if user and safe_str_cmp(user.password, str(sha256(password.encode("utf-8")).hexdigest())): 
        return user

def identity(payload):
    for i in teachers:
        user = User((len(users)+1), i.get("username",""), i.get("password",""))
        users.append(user)
    userid_mapping = {u.id: u for u in users}
    user_id = payload["identity"]
    print("user_id")
    return userid_mapping.get(user_id, None)

