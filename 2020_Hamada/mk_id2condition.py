# coding: utf-8

import json
import random
import itertools

random.seed(123)
C = ["a1b1", "a1b2", "a2b1", "a2b2"]

conditions = list(itertools.permutations(C, 4))
random.shuffle(conditions)

d = {"0": C}
d.update({x+1: list(condition) for x, condition in enumerate(conditions)})
with open("id2conditions.json", "w") as fd:
	json.dump(d, fd, indent=2)

