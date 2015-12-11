"""Scraping sprudge-linked coffee sites"""

import unittest
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

browser = webdriver.Firefox()

def loads_pages_test():
    """tests that it loads pages; loads these back-to-back"""
    browser.get('http://www.google.com')
    return browser.get('python.org')

def return_html(url = "http://www.google.com"):
    """print html of a given URL"""
    browser.get(url)
    content = (browser.page_source).encode("ascii", "ignore")
    return content #gives it back raw
    #return BeautifulSoup(content, "html.parser")

def soup_of_page(url = "http://www.google.com"):
    """get soup of page and parse with lxml"""
    content = return_html(url)
    symbol_free_url = re.sub(r'[^\w]', ' ', url)
    soup = BeautifulSoup(content, "lxml")
    write_page(soup, symbol_free_url)
    """print(datetime.datetime.today())
    print(soup.title)
    for paragraph in soup.find_all("p"):
        print(paragraph.getText())
    for link in soup.find_all("a"):
        print("link: " + link.get('href'))"""


def write_page(soup, symbol_free_url):
    """write page to text file"""
    with open(symbol_free_url +'.txt', 'w') as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("\n" + str(soup.title) + "\n")
        for paragraph in soup.find_all("p"):
            para_text = paragraph.getText()
            #filter by paragraph length in characters
            #can also try by num_words with .split()
            if len(para_text)>25:
                f.write(para_text)
        for link in soup.find_all("a"):
            f.write("\n" + "link: " + link.get('href'))
        f.close()


#print(soup_of_page())
print(soup_of_page("http://www.crummy.com/software/BeautifulSoup/bs4/doc/"))
