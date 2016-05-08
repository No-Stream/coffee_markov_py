"""Scraping sprudge-linked coffee sites"""
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from send2trash import send2trash
from tqdm import tqdm
import os, re, requests, logging, glob, string
import weakref, aiohttp, asyncio
import cProfile
import grequests
import copy
import scrape_sources

#cProfile this file with e.g.:
#python -m cProfile -o 'profile_scrape.pstats' -s 'time' ./requests_scrape_sprudge.py

def remove_symbols(url):
    """"""
    url = str(url)
    return "".join([char if char in string.ascii_letters else " " for char in url ])
    #no need for regex
    #return re.sub(r'[^\w]', ' ', url)

def route_requests(url_list, rec_depth=0):
    """route requests for each top-level domain"""
    logger.debug("urls being routed --> " + str([url for url in url_list]) + "\n \n \n")
    reqs = (grequests.get(url) for url in url_list)
    content = return_html(this_session, url_list[0])
    base_page = BeautifulSoup(content, "lxml")
    soup = base_page.find('body')
    #logger.debug(str(soup))
    for response in grequests.map(reqs):
        try:
            soup.append(copy.copy(BeautifulSoup(response.text, "lxml").find('body')))
        except Exception as e:
            break
            logger.warning("url not handled correctly, line 30 --> " + str(e))
    #logger.debug("concatenated soup --> \n" + str(soup))
    process_async(rec_depth, soup)
    #for url in tqdm(url_list):
    #    process_page(rec_depth, url)

def return_html(session, url):
    """print html of a given URL"""
    try:
        source_html = (this_session.get(url, verify=False, timeout=6.1))
    #content = ''.join([x for x in source_html if not x.isdigit()])
    except requests.exceptions.ReadTimeout as error:
        source_html = ''
        logger.warning("connection timed out at " + str(error))
    return source_html.text

def process_page(rec_depth, url):
    content = return_html(this_session, url)
    symbol_free_url = remove_symbols(url)
    page_object = Scraped_Page(url, symbol_free_url)
    this_page = page_object
    logger.info("processing " + this_page.url)
    soup = BeautifulSoup(content, "lxml")
    this_page.prepare_page(soup, rec_depth)

def process_async(rec_depth, soup):
    filename = "async_output_" + datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S")
    this_page = Scraped_Page(filename, filename)
    this_page.prepare_page(soup, rec_depth)

class Scraped_Page():
    object_count = 0
    ignored_terms = {"twitter", "facebook", "google", "instagram", "apple", "pinterest",
                     "youtube", "account", "login", "register",
                     "cart", "about", "contact", "wholesale", "blog", "careers",
                     "learn", "location", "locations", "tea", "education", "squareup"}

    def __init__(self, url, symbol_free_url):
        self.url = url
        self.symbol_free_url = symbol_free_url
        self.content = ""
        self.timestamp = ""
        self.elements_searched = ["p"]

    def prepare_page(self, soup, rec_depth):
        """logfile if requested"""
        self.write_logfile(soup, False)
        self.handle_duplicate_pages(soup, rec_depth)

    def handle_duplicate_pages(self, soup, rec_depth):
        try:
            if not os.path.isfile("raw_output/" +
            self.symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_") + '.txt'):
                self.write_page_text(soup, rec_depth)
        except FileExistsError:
            logger.info("Attempted to write duplicate page.")

    def write_page_text(self, soup, rec_depth):
        with open( "raw_output/" +
            self.symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_") + '.txt', 'x', encoding="utf-8") as output:
            for element in self.elements_searched:
                if len(soup.find_all(element)) > 0:
                    for paragraph in soup.find_all(element):
                        para_text = paragraph.getText()
                        if len(para_text.split()) > 5: #filter by >8 words
                            try:
                                output.write(para_text + "\n")
                                #logger.debug("paragraph written --> " + str(para_text))
                            #this shouldn't be needed
                            except UnicodeEncodeError:
                                logger.warning("handled unicode encode error, line 72")
                        else:
                            logger.debug("too short: " + para_text)
            output.close()
        self.recur(soup, rec_depth)

    def recur(self, soup, rec_depth):
        """recursive searching of linked pages"""
        rec_depth += 1
        #below no longer works because page is made up of a bunch of concatenated web pages
        parsed_uri = urlparse(self.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        logger.debug("domain = " + domain)

        def has_ignored_terms(text):
            return any(word in Scraped_Page.ignored_terms for word in text.split(" "))

        links_in_page = soup.find_all("a", href=True)
        if rec_depth <= 1 and len(links_in_page) > 0:
            filtered_hrefs = [link.get('href') for link in links_in_page if not has_ignored_terms(remove_symbols(link))]
            filtered_links = filtered_hrefs
            #filtered_links = [domain + link if link[0]=="/" else link for link in filtered_hrefs]
            self.url = "recur " + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S")
            self.symbol_free_url = self.url
            self.attempt_recursive_call(rec_depth, domain, filtered_links)

    def attempt_recursive_call(self, rec_depth, domain, url_list):
        try:
            logger.debug("rec_depth = " + str(rec_depth)+ "; processing " + self.url)
            route_requests(url_list, rec_depth)
        except UnicodeEncodeError:
            logger.warning("handled unicode error, line 108")
        except TypeError:
            logger.warning("handled type error, line 110")
        except requests.exceptions.InvalidSchema as error:
            logger.warning("handled requests.exceptions.InvalidSchema, line 139 --> " + str(error))
        except requests.exceptions.MissingSchema as error:
            logger.warning("handled missing domain, line 141 --> " + str(error))
            #need to handle this above
            """self.url = domain+link.get('href')
            self.symbol_free_url = remove_symbols(self.url)
            if not os.path.isfile(self.symbol_free_url + " " + datetime.now(
            ).strftime("%Y-%m-%d_") + '.txt'):
                logger.debug(
                    "rec_depth = " + str(rec_depth)+"; processing link w/o TLD "
                     + self.symbol_free_url)
                process_page(rec_depth, self.url)"""

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

"""
class Worker:
    """"""TODO: worker class for threaded operation""""""
    def __init__(self, worker_number):
        self.worker_number = worker_number
    worker_page = Scraped_Page()
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.info("Asynchronous scrape begun at " + datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S" + "\n \n \n"))

    profile = cProfile.Profile()
    #profile.enable()

    this_page = None
    this_session = requests.Session()

    route_requests(scrape_sources.COFFEE_PAGES)

    #profile.disable()
    #profile.print_stats(sort='time')
