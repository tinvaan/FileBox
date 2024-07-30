
from os import path


def get(fx):
    cwd = path.dirname(__file__)
    target = path.join(cwd, fx)
    if path.exists(target):
        return target
    raise FileNotFoundError("Fixture file<%s> not found" % fx)
