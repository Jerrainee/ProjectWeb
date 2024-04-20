import datetime
import json

from data import db_session
from data.tests import Test
from data.users import User


def add_tests(db_sess):
    data = []
    for i in ['1', '2', '3', '4']:
        with open(f'json_files/{i}.json', encoding='utf-8') as file:
            f = file.read()
            data.append(json.loads(f))

    test1 = Test(name='Кто вы из 10фм класса?', description='Описание', data=data[0],
                 results="{5: 'Тимур', 4:'Тимурка', 3:'Тимурыч', 2:'Тимууур', 1:'Не Тимур(('}")

    test2 = Test(name='Кто вы из игры dota 2?', description='Очень креативное описание теста', data=data[1],
                 results="{5: 'Инвокер', 4: 'Феникс', 3: 'Анти-маг', 2: 'Шейкер', 1: 'Пудж'}")

    test3 = Test(name='Какая национальная кухня вам подойдет?', description='Очень креативное описание теста',
                 data=data[2],
                 results="{4: 'Европейская кухня', 3: 'Славянская кухня', 2: 'Восточная кухня', 1: 'Американская кухня'}")

    test4 = Test(name='Какая вы Тойота?', description='Очень креативное описание теста',
                 data=data[3],
                 results="{5: 'Skoda Octavia', 4: 'Toyota Supra', 3: 'Toyota Land Cruiser', 2: 'Toyota Century', 1: 'Toyota Corolla'}")

    db_sess.add(test1)
    db_sess.add(test2)
    db_sess.add(test3)
    db_sess.add(test4)
    db_sess.commit()


def add_test_users(db_sess):
    user = User()
    user.name = 'Jerainee'
    user.about = 'ШедевроОписание'
    user.email = 'ilinspavel07@gmail.com'
    user.password = '11111'
    user.created_date = datetime.datetime.now()

    db_sess.add(user)
#  db_sess.commit()
