import json

file = 'test1.json'

class Test():
    def __init__(self, file):
        with open(f'json_files/{file}', encoding="utf-8") as json_file:
            f = json_file.read()
            self.data = json.loads(f)

