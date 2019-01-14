import json

import munch


def open_json(path):
    with open(path) as fd:
        data = json.load(fd)
    return munch.munchify(data)
