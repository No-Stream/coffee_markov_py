"""analyzing lexical diversity with natural language toolkit"""

import nltk, re, pprint
from nltk import word_tokenize
from nltk.corpus import stopwords

"""global text variables below"""
source_file="0CONCAT_2015-12-16_.txt"
coffee_text_raw = open(source_file, "r").read().lower()
stopwords = set(stopwords.words('english'))
coffee_tokens = filter(lambda word: not word in stopwords, word_tokenize(coffee_text_raw))
coffee_porter_stems = [nltk.PorterStemmer().stem(t) for t in coffee_tokens]
coffee_nltk_text = nltk.Text(coffee_porter_stems)
coffee_freqs = nltk.FreqDist(coffee_nltk_text)

def generate_analysis():
    print(coffee_nltk_text.collocations(50))
    #print(nltk.lexical_diversity(coffee_nltk_text))
    print(("Most common words = " + str(coffee_freqs.most_common(50))))
    #coffee_freqs.plot(50, cumulative=True)

generate_analysis()
