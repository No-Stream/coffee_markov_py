"""Scraping sprudge-linked coffee sites"""

import unittest
import datetime
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
    content = return_html(url)
    soup = BeautifulSoup(content, "lxml")
    print(datetime.datetime.today())
    print(soup.title)
    for paragraph in soup.find_all("p"):
        print(paragraph.getText())
    for link in soup.find_all("a"):
        print("link: " + link.get('href'))


#print(soup_of_page())
print(soup_of_page("http://www.crummy.com/software/BeautifulSoup/bs4/doc/"))
