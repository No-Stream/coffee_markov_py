"""Scraping sprudge-linked coffee sites"""

import unittest
import datetime
import re
import requests
from bs4 import BeautifulSoup

def main(url):
    return parse_html_and_write(url)

def return_html(url = "http://www.google.com"):
    """print html of a given URL"""
    source_html = (requests.get(url)).text
    content = (source_html).encode("ascii", "ignore")
    return content #gives it back raw
    #return BeautifulSoup(content, "html.parser")

def parse_html_and_write(url = "http://www.google.com"):
    """get soup of page and parse with lxml"""
    content = return_html(url)
    symbol_free_url = re.sub(r'[^\w]', ' ', url)
    soup = BeautifulSoup(content, "lxml")
    #wrapping in write function
    write_page(soup, symbol_free_url)


def write_page(soup, symbol_free_url):
    """write page to text file"""
    with open(
        symbol_free_url + " " + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + '.txt', 'w') as f:
        #f.write(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        #f.write("\n" + str(soup.title) + "\n")
        if len(soup.find_all("p"))>0:
            for paragraph in soup.find_all("p"):
                para_text = paragraph.getText()
                if len(para_text.split())>5: #filter by >5 words
                    f.write(para_text)
        if len(soup.find_all("a"))>0:
            for link in soup.find_all("a"):
                f.write('a clause fired')
                try: 
                    f.write("\n" + "link: " + link.get('href'))
                except TypeError:
                    pass
        f.close()


main('http://www.gutenberg.org/files/216/216-h/216-h.htm')
#print(soup_of_page("http://www.crummy.com/software/BeautifulSoup/bs4/doc/"))
