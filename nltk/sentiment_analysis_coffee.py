"""analyze sentiment using super simple counting model
positive & negative valences pulled from bing lu et al."""

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import word_valence_list

#run & profile with e.g. python -m cProfile -s 'time' sentiment_analysis_coffee.py > val_profile.txt 2>&1

"""global text variables below"""
source_file = "0CONCAT_2015-12-16_.txt"
coffee_text_raw = open("0CONCAT_2015-12-16_.txt", "r").read().lower()
stopwords = set(stopwords.words('english'))
tokenized = word_tokenize(coffee_text_raw)

pos_words = word_valence_list.positive_words
neg_words = word_valence_list.negative_words

input_ = tokenized

def imp_count_valence(input_,pos_words,neg_words):
    """simple, inefficient iterative & imperative solution to counting words"""
    pos_count = 0
    neg_count = 0
    for word in input_:
        if word in pos_words:
            pos_count += 1
        if word in neg_words:
            neg_count += 1
    print("pos_count = " + str(pos_count) + " neg_count = " + str(neg_count))
    print("ratio pos:neg " + str(pos_count/neg_count))

def func_count_valence(input_,pos_words,neg_words):
    """hopefully slightly more efficient functional solution"""
    valent_words = [word for word in input_ if word in pos_words or word in neg_words]
    filter_pos = [word for word in valent_words if word in pos_words]
    filter_neg = [word for word in valent_words if word in neg_words]
    print(filter_pos)
    print(filter_neg)

imp_count_valence(input_,pos_words,neg_words)
#func_count_valence(input_,pos_words,neg_words)
