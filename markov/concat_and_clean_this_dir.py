import glob
from send2trash import send2trash
from datetime import datetime

read_files = glob.glob("*.txt")

def delete_empty_txts():
    """delete all empty text files first"""
    for f in read_files:
        delete_bool = True
        with open(f, "r+", encoding="utf-8") as infile:
            for line in infile:
                if line.rstrip():
                    delete_bool = False
            infile.close()
        if delete_bool:
            send2trash(f)

def glob_append():
    """use glob to concatenate files"""
    with open("CONCAT_MARKOVIAN_"+datetime.now().strftime(
        "%Y-%m-%d_"), "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())

if __name__ == '__main__':
    delete_empty_txts()
    glob_append()
