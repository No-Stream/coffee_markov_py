"""Scraping sprudge-linked coffee sites"""
import unittest
import datetime
import re
#import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


class Tests(unittest.TestCase):
    """unittests; TODO"""
    def test_return_html(self):
        """tests that you get html; TODO"""
        self.assertEqual(1, 1)

def main(url_list):
    """Let's get shit started"""
    for url in url_list:
        #print(url)
        return parse_html_and_write(url)

def return_html(url="http://www.google.com"):
    """print html of a given URL"""
    source_html = (requests.get(url)).text
    content = (source_html).encode("ascii", "ignore")
    return content #gives it back raw
    #return BeautifulSoup(content, "html.parser")

def parse_html_and_write(url="http://www.google.com", rec_depth=0):
    """get soup of page and parse with html.parser; lxml didn't find all"""
    content = return_html(url)
    symbol_free_url = re.sub(r'[^\w]', ' ', url)
    soup = BeautifulSoup(content, "html.parser")
    #log_links_on_page(soup, symbol_free_url)
    #wrapping in write function
    write_page(soup, symbol_free_url, url, rec_depth)


def write_page(soup, symbol_free_url, url, rec_depth):
    """write page to text file"""
    write_logfile(soup, True)
    #TODO: makedir for log & scape data
    #os.makedirs('test/', exist_ok=True)
    elements_searched = ["p", "span"]
    with open(
        symbol_free_url + " " + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + '.txt', 'w') as output:
        for element in elements_searched:
            if len(soup.find_all(element)) > 0:
                for paragraph in soup.find_all(element):
                    para_text = paragraph.getText()
                    if len(para_text.split()) > 5: #filter by >5 words
                        output.write(para_text)
                    else:
                        print("this wasn't long enough: " + para_text)
        recur(soup, rec_depth, url)
        output.close()

def recur(soup, rec_depth, url):
    """recursive searching of linked pages
    TODO: separate this function and refactor"""
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    print("domain = " + domain)
    if rec_depth < 1 and len(soup.find_all("a")) > 0:
        for link in soup.find_all("a", href=True):
            try:
                print("recurring w/ link = " + link.get('href'))
                try:
                    parse_html_and_write(link.get('href'), rec_depth=1)
                #TODO: clean up catch-all exception-catcher
                except Exception:
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



"""full coffee sites for
TODO: recursive scraping of full sites by regex of *URL*"""
SITES = [
    "http://49thcoffee.com/",
    "http://barnine.us/",
    "https://bluebottlecoffee.com/",
    "http://ceremonycoffee.com/",
    "https://counterculturecoffee.com/",
    "http://www.dogwoodcoffee.com/",
    "http://www.equatorcoffees.com/",
    "http://www.fiveelephant.com/",
    "http://www.intelligentsiacoffee.com/",
    "http://www.joenewyork.com/",
    "http://kaldiscoffee.com/",
    "http://www.lacolombe.com/",
    "http://madcapcoffee.com/",
    "http://mrespresso.com/",
    "http://theroasters.com.au/",
    "http://www.olympiacoffee.com/",
    "http://www.onyxcoffeelab.com/",
    "http://www.pcpfx.com/",
    "https://www.philsebastian.com/",
    "http://populace.coffee/",
    "http://www.ptscoffee.com/",
    "http://www.reanimatorcoffee.com/",
    "http://revelatorcoffee.com/",
    "https://www.sharecoffeeroasters.com/",
    "http://spyhousecoffee.com/",
    "http://www.stumptowncoffee.com/",
    "http://www.tobysestate.com.au/",
    "http://www.tonyscoffee.com/",
    "http://www.vervecoffeeroasters.com/",
    "http://wateravenuecoffee.com/",
]

"""products pages for coffee roasters"""
COFFEE_PAGES = [
    "http://49thcoffee.com/collections/shop",
    "http://barnine.us/collections/all",
    "https://bluebottlecoffee.com/store/coffee",
    "http://store.ceremonycoffee.com/coffees/",
    "https://counterculturecoffee.com/store/coffee:",
    "http://www.dogwoodcoffee.com/collections/coffee"

]

#main('http://www.gutenberg.org/files/216/216-h/216-h.htm')
#main(["http://www.crummy.com/software/BeautifulSoup/bs4/doc/"])
#main(COFFEE_PAGES)
main(["http://49thcoffee.com/collections/shop"])
#main(["http://49thcoffee.com/products/santa-barbara-sampler"])
