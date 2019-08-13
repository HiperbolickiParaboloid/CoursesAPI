from werkzeug.security import safe_str_cmp
from Teachers import mycol_teachers


class User():
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password
    def __str__(self):
        return f'username: {self.username}, password: {self.password}, _id: {self.id}'


br = 1
users = [ User(1, "admin", "admin")
]
teachers = list(mycol_teachers.find())
for i in teachers:
    user = User((len(users)+1), i.get("username",""), i.get("password",""))
    users.append(user)
for i in users:
    print (i)

username_mapping = {u.username: u for u in users}
userid_mapping = {u.id: u for u in users}

def authenticate(username, password):
    user = username_mapping.get(username, None)
    if user and safe_str_cmp(user.password.encode("utf-8"), password.encode("utf-8")): # sigurniji nacin za provjeru stringovacd
        return user

def identity(payload):
    user_id = payload["identity"]
    return userid_mapping.get(user_id, None)

