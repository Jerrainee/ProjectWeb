import datetime
import json

import wtforms
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user

from data import db_session
from data.tests import Test
from data.users import User


def add_tests(db_sess):
    data = []
    for i in [1, 2]:
        with open(f'json_files/{i}.json', encoding='utf-8') as file:
            data.append(json.loads(file.read()))

    test = Test()
    test.name = 'Кто вы из 10фм класса?'
    test.description = 'Описание'
    test.data = data[0]
    test.results = "{5: 'Тимур', 4:'Тимурка', 3:'Тимурыч', 2:'Тимууур', 1:'Не Тимур(('}"

    test2 = Test(name='Кто вы из игры dota 2?', description='Очень креативное описание теста', data=data[1],
                 results="{5: 'Инвокер', 4: 'Феникс', 3: 'Анти-маг', 2: 'Шейкер' 1: 'Пудж')")

    db_sess.add(test2)
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
