"""Scraping sprudge-linked coffee sites"""

import unittest
import datetime
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class Tests(unittest.TestCase):
    """unittests; TODO"""
    def test_return_html(self):
        """tests that you get html; TODO"""
        self.assertEqual(1, 1)

def main(url_list):
    """Let's get shit started"""
    for url in url_list:
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
    write_page(soup, symbol_free_url, url)


def write_page(soup, symbol_free_url, url, rec_depth = 0):
    """write page to text file"""
    write_logfile(soup, True)
    with open(
        symbol_free_url + " " + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + '.txt', 'w') as f:
        if len(soup.find_all("p"))>0:
            for paragraph in soup.find_all("p"):
                para_text = paragraph.getText()
                if len(para_text.split())>5: #filter by >5 words
                    f.write(para_text)
        def log_links_on_page(soup, default = True):
            if not default:
                if len(soup.find_all("a"))>0:
                    for link in soup.find_all("a", href=True):
                        try:
                            f.write("\n" + "link: " + link.get('href'))
                        except TypeError:
                            pass
        def recur(soup, default = True):
            parsed_uri = urlparse(url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            print("parsed: " + domain)
            if default and rec_depth < 2 and len(soup.find_all("a"))>0:
                for link in soup.find_all("a", href=True):
                    try:
                        if re.match(domain + r".[^\s]*", link.get('href')):
                            print(link.get('href'))
                            #parse_html_and_write(link.get('href'))
                    except TypeError:
                        pass
        log_links_on_page(soup, False)
        recur(soup, True)
        rec_depth += 1
        f.close()

def write_logfile(soup, default = True):
    if default:
        with open(
            "SCRAPE_LOG" + " " + datetime.datetime.now().strftime(
                "%Y-%m-%d") + '.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            f.write("\n" + str(soup.title) + "\n" + "\n")
            f.close()



"""full coffee sites for
TODO: recursive scraping of full sites by regex of *URL*"""
sites = [
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
coffee_pages = [
    "http://49thcoffee.com/collections/shop",
    "http://barnine.us/collections/all",
]

#main('http://www.gutenberg.org/files/216/216-h/216-h.htm')
main(["http://www.crummy.com/software/BeautifulSoup/bs4/doc/"])
