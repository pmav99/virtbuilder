import json


def open_json(path):
    with open(path) as fd:
        data = json.load(fd)
    return data
