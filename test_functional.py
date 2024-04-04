import json
from forms.test_form import TestForm
file = 'test1.json'


class Test():
    def __init__(self, file):
        with open(f'json_files/{file}', encoding="utf-8") as json_file:
            f = json_file.read()
            self.data = json.loads(f)
            print(self.data)

    def run(self, n):
        if n == len(self.data):
            pass  # тест пройден
        else:
            question = self.data[n]['question']
            answers = self.data[n]['answers']
            print([(i, i) for i in answers.keys()])

            return question, answers


test = Test(file)
test.run(0)
