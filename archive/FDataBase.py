import math
import time
import sqlite3
import base64


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMessages(self):
        sql = '''SELECT * FROM support'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []

    def getNews(self):
        try:
            self.__cur.execute(f"SELECT id, title, txt, img FROM news ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []

    def addNews(self, title, txt, img):
        try:
            b64_img = base64.b64encode(img.read()).decode('utf-8')
            img = f'<img src="data:image/png;base64,{b64_img}">'
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO news VALUES(NULL, ?, ?, ?, ?)", (title, txt, tm, img))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления новости в БД")
            return False
        return True

    def getUser(self, id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def addUser(self, id, hash):
        try:
            self.__cur.execute(f'UPDATE users SET psw=\"{hash}\" WHERE id={id}')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД", e)
            return False
        return True

    def getUsers(self):
        try:
            self.__cur.execute(f'SELECT * FROM users')
            res = self.__cur.fetchall()
            if not res:
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def sendMsg(self, id, msg):
        user = self.getUser(id)
        tm = time.time()
        if user:
            self.__cur.execute("INSERT INTO support VALUES(?, ?, ?)", (id, msg, tm))
            self.__db.commit()
        else:
            return False
        return True

    def getMsgs(self):
        try:
            self.__cur.execute(f"SELECT id, msg FROM support ORDER BY tag DESC")
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []