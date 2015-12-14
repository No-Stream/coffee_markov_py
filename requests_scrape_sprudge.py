"""Scraping sprudge-linked coffee sites"""
import unittest
import datetime
import re
#import os.path
from string import printable
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import scrape_sources


class Tests(unittest.TestCase):
    """unittests; TODO"""
    def test_return_html(self):
        """tests that you get html; TODO"""
        self.assertEqual(1, 1)

def main(url_list, rec_depth=0):
    """Let's get shit started"""
    for url in url_list:
        #print(url)
        return parse_html_and_write(url, rec_depth)

def return_html(url):
    """print html of a given URL"""
    source_html = (requests.get(url)).text
    #content = (source_html).encode("ascii", "ignore")
    content = ''.join([x for x in source_html if x in printable])
    return content #gives it back raw
    #return BeautifulSoup(content, "html.parser")

def parse_html_and_write(url, rec_depth):
    """get soup of page and parse with html.parser; lxml didn't find all"""
    content = return_html(url)
    symbol_free_url = re.sub(r'[^\w]', ' ', url)
    print("symbol_free_url= " + symbol_free_url)
    soup = BeautifulSoup(content, "html.parser")
    #log_links_on_page(soup, symbol_free_url)
    #wrapping in write function
    write_page(soup, symbol_free_url, url, rec_depth)


def write_page(soup, symbol_free_url, url, rec_depth):
    """write page to text file"""
    write_logfile(soup, True)
    #TODO: makedir for log & scape data
    #os.makedirs('test/', exist_ok=True)
    elements_searched = ["p"]
    try:
        with open(
            symbol_free_url + " " + datetime.datetime.now().strftime(
                "%Y-%m-%d_") + '.txt', 'x') as output:
            for element in elements_searched:
                if len(soup.find_all(element)) > 0:
                    for paragraph in soup.find_all(element):
                        para_text = paragraph.getText()
                        if len(para_text.split()) > 5: #filter by >5 words
                            try:
                                output.write(para_text + "\n")
                            #soup has already been filtered for printable
                            #and yet this excpetion handling is needed...
                            except UnicodeEncodeError:
                                pass
                        else:
                            print("too short: " + para_text)
            recur(soup, rec_depth, url)
            output.close()
    #TODO: optimize by moving handling of redundant files to recur clause
    except FileExistsError:
        pass #file already exists; skipping

def recur(soup, rec_depth, url):
    """recursive searching of linked pages
    TODO: separate this function and refactor"""
    rec_depth += 1
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    print("domain = " + domain)
    if rec_depth <= 2 and len(soup.find_all("a")) > 0:
        for link in soup.find_all("a", href=True):
            try:
                print("rec_depth = " + str(rec_depth)+"; processing " + link.get('href'))
                parse_html_and_write(link.get('href'), rec_depth)
            except requests.exceptions.MissingSchema:
                #try:
                parse_html_and_write(domain+link.get('href'), rec_depth)
                #except:
                #    print("undefined error, line 79")
            except UnicodeEncodeError:
                pass
            except TypeError:
                pass

def log_links_on_page(soup, symbol_free_url):
    """print links on page to log file"""
    with open("LINKS: " + symbol_free_url + " " + datetime.datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S") + '.txt', 'w') as links_log:
        if len(soup.find_all("a")) > 0:
            for link in soup.find_all("a", href=True):
                try:
                    links_log.write("\n" + "link: " + link.get('href'))
                except TypeError:
                    pass

def write_logfile(soup, default=True):
    """write logfile of scraping operation"""
    if default:
        with open(
            "SCRAPE_LOG" + " " + datetime.datetime.now().strftime(
                "%Y-%m-%d") + '.txt', 'a') as logfile:
            logfile.write(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            logfile.write("\n" + str(soup.title) + "\n" + "\n")
            logfile.close()


#main('http://www.gutenberg.org/files/216/216-h/216-h.htm')
#main(["http://www.crummy.com/software/BeautifulSoup/bs4/doc/"])
#main(COFFEE_PAGES)
#main(["http://49thcoffee.com/collections/shop"])
#main(["http://49thcoffee.com/products/santa-barbara-sampler"])
main(scrape_sources.EXAMPLE)
#main(scrape_sources.COFFEE_PAGES)
