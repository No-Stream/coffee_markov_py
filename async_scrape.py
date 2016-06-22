"""Scraping sprudge-linked coffee sites"""
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from send2trash import send2trash
import os, re, requests, logging, glob, string
import weakref, aiohttp, asyncio
import cProfile
import grequests
import copy
import scrape_sources

#cProfile this file with e.g.:
#python -m cProfile -o 'profile_scrape.pstats' -s 'time' ./requests_scrape_sprudge.py

#TODO: below three funcs should be refactored into page class

def get_domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    logger.debug("domain = " + domain)
    return domain

def url_includes_domain(url):
    return str(url).startswith("http")

def remove_symbols(url):
    """"""
    url = str(url)
    return "".join([char if char in string.ascii_letters else " " for char in url])

def route_requests(urls_and_domains, rec_depth=0):
    """route requests for each top-level domain"""

    this_page.timestamp = "async_output_" + datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S")
    #this_page.links_in_page = []

    logger.debug("(urls,domains) being routed --> " + str([url for url in urls_and_domains]) + "\n \n \n")
    url_list = {tuple_[0] if url_includes_domain(tuple_[0]) else tuple_[1]+tuple_[0] for tuple_ in urls_and_domains}

    logger.debug("Following these links: " + str(url_list) + "\n")

    #TODO: """extract function _def_ make_requests(urls):"""
    reqs = (grequests.get(url, timeout=12.1) for url in url_list)
    if this_page.content == "":
        this_page.content = return_html("http://www.this-page-intentionally-left-blank.org/")
    base_page = BeautifulSoup(this_page.content, "lxml")
    soup = base_page.find('body')

    for url,response in zip(url_list,grequests.map(reqs)):
        if url is not None and response is not None:
            logger.debug("Getting links from " + url)
            domain = get_domain(url)
            new_soup = BeautifulSoup(response.text, "lxml").find('body')
            new_links = new_soup.find_all("a", href=True)
            link_refs = {link.get('href') for link in new_links if link is not None}
            #logger.debug('link refs w/o symbols = ' + str(link_refs))
            filtered_new_links = {link for link in link_refs if not this_page.has_ignored_terms(remove_symbols(link))}
            logger.debug("Found links in above page: " + str(filtered_new_links))
            for link in filtered_new_links:
                this_page.links_in_page.add((link,domain))
            soup.append(copy.copy(BeautifulSoup(response.text, "lxml").find('body')))

    this_page.prepare_page(soup, rec_depth)

def return_html(url):
    """print html of a given URL"""
    try:
        source_html = (this_session.get(url, verify=False, timeout=6.1))
    #content = ''.join([x for x in source_html if not x.isdigit()])
    except requests.exceptions.ReadTimeout as error:
        source_html = ''
        logger.warning("connection timed out at " + str(error))
    return source_html.text


class Scraped_Page():
    object_count = 0
    ignored_terms = {"twitter", "facebook", "google", "instagram", "apple", "pinterest",
                     "youtube", "account", "login", "register", "flickr", "pdf",
                     "cart", "about", "contact", "wholesale", "blog", "careers", "jobs",
                     "learn", "location", "locations", "tea", "education", "squareup",
                     "mailto", "javascript", "flash", "terms", "privacy", "shipping",
                     "press", "return", "returns", "jpg", "jpeg", "conditions", "support"}

    def __init__(self):
        self.url = ""
        self.symbol_free_url = ""
        self.content = ""
        self.timestamp = ""
        self.links_in_page = set()
        self.elements_searched = ["p"]

    def prepare_page(self, soup, rec_depth):
        """logfile if requested"""
        self.write_logfile(soup, False)
        self.write_page_text(soup, rec_depth)

    def write_page_text(self, soup, rec_depth):
        with open( "raw_output/" +
            self.symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S") + '.txt', 'x', encoding="utf-8") as output:
            for element in self.elements_searched:
                if len(soup.find_all(element)) > 0:
                    for paragraph in soup.find_all(element):
                        para_text = paragraph.getText()
                        if len(para_text.split()) > 8: #filter by >8 words
                            try:
                                output.write(" " + para_text + "\n")
                            except UnicodeEncodeError:
                                logger.warning("handled unicode encode error, line 118")
            output.close()
        self.recur(soup, rec_depth)

    def has_ignored_terms(self, text):
        return any(word in Scraped_Page.ignored_terms for word in text.split(" "))

    def recur(self, soup, rec_depth):
        """recursive searching of linked pages"""
        rec_depth += 1

        if rec_depth <= 1 and len(self.links_in_page) > 0:
            self.url = "recur " + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S")
            self.symbol_free_url = self.url
            self.attempt_recursive_call(rec_depth)
        elif len(self.links_in_page) == 0:
            logger.info("Stopping recursion; no links left to follow.")
        elif rec_depth >= 2:
            logger.info("Stopping recursion; recursion depth = " + str(rec_depth))

    def attempt_recursive_call(self, rec_depth):
        try:
            logger.debug("rec_depth = " + str(rec_depth)+ "; processing " + self.url)
            route_requests(self.links_in_page, rec_depth)
        except UnicodeEncodeError:
            logger.warning("handled unicode error, line 108")
        except requests.exceptions.InvalidSchema as error:
            logger.warning("handled requests.exceptions.InvalidSchema, line 139 --> " + str(error))
        except requests.exceptions.MissingSchema as error:
            logger.warning("handled missing domain, line 141 --> " + str(error))

    def delete_irrelevant_texts(self):
        read_files = glob.iglob("/raw_output/*.txt")
        for f in read_files:
            with open(f, "r+", encoding="utf-8") as infile:
                delete_this_file = True
                for line in infile:
                    if line.rstrip():
                        delete_this_file = False
                if sum([1 for word in os.path.basename(infile) if word in Scraped_Page.ignored_terms]) > 0:
                    delete_this_file = True
                infile.close()
            if delete_this_file:
                send2trash(f)

    def log_links_on_page(self, soup):
        """print links on page to log file"""
        with open("LINKS: " + self.symbol_free_url + " " + datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + '.txt', 'w') as links_log:
            if len(soup.find_all("a")) > 0:
                for link in soup.find_all("a", href=True):
                    try:
                        links_log.write("\n" + "link: " + link.get('href'))
                    except TypeError:
                        pass

    def write_logfile(self, soup, default=True):
        """write logfile of scraping operation"""
        if default:
            with open("raw_output/" +
                "SCRAPE_LOG" + " " + datetime.now().strftime(
                    "%Y-%m-%d") + '.txt', 'a', encoding="utf-8") as logfile:
                logfile.write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                logfile.write("\n" + str(soup.title) + "\n" + "\n")
                logfile.close()



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Asynchronous scrape begun at " + datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S" + "\n \n \n"))

    profile = cProfile.Profile()
    profile.enable()

    this_page = Scraped_Page()
    this_session = requests.Session()

    initial_urls_and_domains = [(url, get_domain(url)) for url in scrape_sources.COFFEE_PAGES]

    route_requests(initial_urls_and_domains)

    profile.disable()
    profile.print_stats(sort='time')
