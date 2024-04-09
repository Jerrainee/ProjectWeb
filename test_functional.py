import json
from forms.test_form import TestForm


class Test():
    def __init__(self, i):
        with open(f'json_files/{i}.json', encoding="utf-8") as json_file:
            f = json_file.read()
            self.data = json.loads(f)
            print(self.data)

    def run(self, n):
        if n == len(self.data):
            return 1    # тест пройден
        else:
            question = self.data[n]['question']
            answers = self.data[n]['answers']
            print([(i, i) for i in answers.keys()])

            return question, answers


test = Test(0)
test.run(0)
