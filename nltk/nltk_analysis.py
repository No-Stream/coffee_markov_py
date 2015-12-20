"""analyzing lexical diversity with natural language toolkit"""

import nltk, re, pprint
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
import cProfile

#profiling this script with python -m cProfile -s 'time' nltk_analysis.py > profile.txt 2>&1

excluded_terms = [
"javascript", "browser", "website", "enable", "enabled", "disable", "disabled"
]

def generate_text_analysis():
    print(coffee_nltk_text.collocations(50))
    #print(nltk.lexical_diversity(coffee_nltk_text))

def generate_freq_analysis():
        print(("Most common words = " + str(coffee_freqs.most_common(50))))
        #coffee_freqs.plot(50, cumulative=True)

def generate_sentiment_analysis():
    pass

"""global text variables below"""
source_file = "0CONCAT_2015-12-16_.txt"
coffee_text_raw = open(source_file, "r").read().lower()
stopwords = set(stopwords.words('english'))
tokenized = word_tokenize(coffee_text_raw)
coffee_tokens = [word for word in tokenized if word not in stopwords and word not in excluded_terms]
coffee_porter_stems = [nltk.PorterStemmer().stem(t) for t in coffee_tokens]
coffee_nltk_text = nltk.Text(coffee_porter_stems)

generate_text_analysis()

coffee_freqs = nltk.FreqDist(coffee_nltk_text)

generate_freq_analysis()

generate_sentiment_analysis()


#TODO: sentiment analysis
