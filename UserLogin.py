from FDataBase import *


class UserLogin:

    def fromDB(self, id, db):
        self.__user = db.getUser(id)
        self.id = id
        return self

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def is_admin(self):
        if self.__user['IsAdmin'] == 1:
            return True
        return False

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])