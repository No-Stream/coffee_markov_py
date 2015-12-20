"""split /n separated to text list
from http://stackoverflow.com/questions/13169725/how-to-convert-a-string-that-has-newline-characters-in-it-into-a-list-in-python"""

import glob

filenames = ["positive-words.txt", "negative-words.txt"]

def convert_to_list(filename):
    for file_ in filenames:
        text = open(file_, "r").read().lower()
        word_list = text.splitlines()
        word_string = str(word_list)
        with open("list_" + file_, "w+") as outfile:
            outfile.write(word_string)
        #file_.close()

convert_to_list(filenames)
