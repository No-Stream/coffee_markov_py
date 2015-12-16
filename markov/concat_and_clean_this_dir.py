"""script to concatenate all text files in a directory
thank you based stackoverflow"""

import os
import glob
from datetime import datetime

folder_location = os.path.expanduser(
"~/Documents/programming/coffee_markov_py/markov/12-13-2015_Singlethread_Ex")

read_files = glob.glob("*.txt")

def glob_append():
    with open("0CONCAT_"+datetime.now().strftime(
        "%Y-%m-%d_"), "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())

glob_append()
