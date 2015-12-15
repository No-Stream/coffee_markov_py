"""again based on an example from onthelambda.com"""

import pickle
import random
import re

chain = pickle.load(open("chain.p", "rb"))

new_review = []
sword1 = re.match(r"A-Z", chain)
sword2 = re.match(r".", chain)

while True:
    sword1, sword2 = sword2, random.choice(chain[(sword1, sword2)])
    if sword2 == "END":
        break
    new_review.append(sword2)

print(' '.join(new_review))
