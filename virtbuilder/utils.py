import json

import ruamel.yaml


def load_yaml(path):
    yml = ruamel.yaml.YAML(typ="safe", pure=True)  # 'safe' load and dump
    data = yml.load(path.read_text())
    return data


def load_json(path):
    with open(path) as fd:
        data = json.load(fd)
    return data
