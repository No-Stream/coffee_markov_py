"""Scraping sprudge-linked coffee sites"""
import unittest
import logging
#import multiprocessing
#from time import sleep
from datetime import datetime
from re import sub
import os.path
import os
from string import printable
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import scrape_sources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tests(unittest.TestCase):
    """unittests; TODO"""
    def test_return_html(self):
        """tests that you get html; TODO"""
        self.assertEqual(1, 1)

def main(url_list, rec_depth=0):
    """Let's get shit started"""
    #if __name__ == '__main__':
    #    multiprocessing.freeze_support()
    #use of shared session dramatically reduces 429 errors and increases speed
    this_session = requests.Session()
    for url in url_list:
        parse_html_and_write(url, rec_depth, this_session)

def return_html(url, this_session):
    """print html of a given URL"""
    source_html = (this_session.get(url)).text
    #content = (source_html).encode("ascii", "ignore")
    content = ''.join([x for x in source_html if x in printable and not x.isdigit()])
    return content #gives it back raw
    #return BeautifulSoup(content, "html.parser")

def parse_html_and_write(url, rec_depth, this_session):
    """get soup of page and parse with html.parser; lxml didn't find all"""
    content = return_html(url, this_session)
    symbol_free_url = remove_symbols(url)
    logger.info("symbol_free_url= " + symbol_free_url)
    soup = BeautifulSoup(content, "html.parser")
    #log_links_on_page(soup, symbol_free_url)
    #wrapping in write function
    write_page(soup, symbol_free_url, url, rec_depth, this_session)


def write_page(soup, symbol_free_url, url, rec_depth, this_session):
    """write page to text file"""
    write_logfile(soup, True)
    #TODO: makedir for log & scape data
    #os.makedirs('test/', exist_ok=True)
    elements_searched = ["p"]
    try:
        with open(
            symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_") + '.txt', 'x') as output:
            for element in elements_searched:
                if len(soup.find_all(element)) > 0:
                    for paragraph in soup.find_all(element):
                        para_text = paragraph.getText()
                        if len(para_text.split()) > 8: #filter by >8 words
                            try:
                                output.write(para_text + "\n")
                            #soup has already been filtered for printable
                            #and yet this excpetion handling is needed...
                            except UnicodeEncodeError:
                                logger.warning("handled unicode encode error, line 72")
                        #else:
                        #    logger.debug("too short: " + para_text)
            recur(soup, rec_depth, url, this_session)
            output.close()
    except FileExistsError:
        pass #file already exists; skipping

def recur(soup, rec_depth, url, this_session):
    """recursive searching of linked pages
    TODO: separate this function and refactor"""
    rec_depth += 1
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    logger.info("domain = " + domain)
    #TODO: ignore these terms:
    ignored_terms = ["twitter", "facebook", "google", "instagram", "apple", "pinterest",
                     "youtube", "pinterest", "account", "login", "register",
                     "cart", "about", "contact", "wholesale", "blog", "careers",
                     "learn", "location", "locations", "tea", "education", "squareup"]
    def has_ignored_terms(text):
        """see above"""
        return any(word in ignored_terms for word in text.split(" "))
    if rec_depth <= 2 and len(soup.find_all("a")) > 0:
        #multiprocessing.freeze_support()
        #rec_pool = multiprocessing.Pool(4)
        for link in soup.find_all("a", href=True):
            url = link.get('href')
            symbol_free_url = remove_symbols(url)
            if has_ignored_terms(symbol_free_url):
                logger.info("skipped ignored_term" + "word = ??? " + "url = " + symbol_free_url)
            elif not os.path.isfile(symbol_free_url + " " + datetime.now().strftime(
                    "%Y-%m-%d_") + '.txt'):
                try:
                    logger.info("rec_depth = " + str(rec_depth)+"; processing " + url)
                    #trying sleep here to reduce 429 errors
                    #sleep(1)
                    #rec_pool.apply_async(parse_html_and_write(url, rec_depth, this_session))
                    parse_html_and_write(url, rec_depth, this_session)
                except UnicodeEncodeError:
                    logger.warning("handled unicode error, line 108")
                except TypeError:
                    logger.warning("handled type error, line 110")
                except requests.exceptions.InvalidSchema:
                    logger.warning("handled requests.exceptions.InvalidSchema, line 112")
                except requests.exceptions.MissingSchema:
                    url = domain+link.get('href')
                    symbol_free_url = remove_symbols(url)
                    if not os.path.isfile(symbol_free_url + " " + datetime.now(
                    ).strftime("%Y-%m-%d_") + '.txt'):
                        #trying sleep here to reduce 429 errors
                        #sleep(1)
                        #rec_pool.apply_async(parse_html_and_write(url, rec_depth, this_session))
                        logger.info(
                            "rec_depth = " + str(rec_depth)+"; processing link w/o TLD " + url)
                        parse_html_and_write(url, rec_depth, this_session)


def log_links_on_page(soup, symbol_free_url):
    """print links on page to log file"""
    with open("LINKS: " + symbol_free_url + " " + datetime.now().strftime(
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
            "SCRAPE_LOG" + " " + datetime.now().strftime(
                "%Y-%m-%d") + '.txt', 'a') as logfile:
            logfile.write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            logfile.write("\n" + str(soup.title) + "\n" + "\n")
            logfile.close()

def remove_symbols(url):
    """remove symbols from a URL"""
    symbol_free_url = sub(r'[^\w]', ' ', url)
    return symbol_free_url

#main('http://www.gutenberg.org/files/216/216-h/216-h.htm')
#main(["http://www.crummy.com/software/BeautifulSoup/bs4/doc/"])
#main(["http://49thcoffee.com/collections/shop"])
#main(scrape_sources.EXAMPLE)
main(scrape_sources.COFFEE_PAGES)
