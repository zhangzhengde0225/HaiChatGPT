


class UserManager(object):
    def __init__(self) -> None:
        self._users = {}

    @property
    def users(self):
        return self._users
    
    def add_user(self, user, password):
        self._users[user] = password

    def remove_user(self, user):
        del self._users[user]

    def check_password(self, user, password):
        return self._users.get(user) == password
    
    def is_exist(self, user):
        return user in self._users.keys()
