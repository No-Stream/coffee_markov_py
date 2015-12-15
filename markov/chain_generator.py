"""simple markov chain; slightly modified from onthelabmda.com"""
import pickle

FILE_ = open("markov_source.txt", "r")

CHAIN = {}

def generate_trigram(words):
    """generate markov trigram"""
    if len(words) < 3:
        return
    for i in range(len(words) - 2):
        yield (words[i], words[i+1], words[i+2])

for line in FILE_.readlines():
    words = line.split()
    for word1, word2, word3 in generate_trigram(words):
        key = (word1, word2)
        if key in CHAIN:
            CHAIN[key].append(word3)
        else:
            CHAIN[key] = [word3]

pickle.dump(CHAIN, open("chain.p", "wb"))
