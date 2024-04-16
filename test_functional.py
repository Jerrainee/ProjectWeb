import json

from data import db_session
from data.tests import Test
from flask import redirect, abort

from forms.test_form import TestForm


class TestFunc():
    def __init__(self, test):
        test = str(test).split(';;')
        print(test[3])
        self.id = test[0]
        self.name = test[1]
        self.desc = test[2]
        self.data = [eval(i + '}') for i in (test[3])[1:-2].split('}, ')]
        self.res = eval(test[4])

    def run(self, n):
        if n == len(self.data):
            return '1'
        elif n > len(self.data):
            return abort(400)
        else:
            question = self.data[n]['question']
            answers = self.data[n]['answers']

            return question, answers


    def result(self, cur_res):
        dct_data = {}
        for i in cur_res:
            dct_data[i] = cur_res.count(i)
        dct_res = sorted(dct_data.items(), key=lambda x: x[1], reverse=True)
        return self.res[dct_res[0][0]]


