"""Scraping sprudge-linked coffee sites"""
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from send2trash import send2trash
from tqdm import tqdm
import os, re, requests, logging, scrape_sources, glob, string, multiprocessing
import weakref, aiohttp, asyncio


def remove_symbols(url):
    """"""
    url = str(url)
    return "".join([char if char in string.ascii_letters else " " for char in url ])
    #no need for regex
    #return re.sub(r'[^\w]', ' ', url)

def route_requests(url_list, rec_depth=0):
    """route requests for each top-level domain"""
    for url in tqdm(url_list):
        process_page(rec_depth, url)

def return_html(session, url):
    """print html of a given URL"""
    source_html = (this_session.get(url)).text
    content = ''.join([x for x in source_html if not x.isdigit()])
    return content


async def async_return_html(session,url):
    with aiohttp.Timeout(10):
        async with this_session.get(url) as response:
            return await response.text()

def process_page(rec_depth, url):
    content = return_html(this_session, url)
    symbol_free_url = remove_symbols(url)
    page_object = Scraped_Page(url, symbol_free_url)
    this_page = page_object
    logger.info("processing " + this_page.url)
    soup = BeautifulSoup(content, "html.parser")
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

    def prepare_page(self, soup, rec_depth):
        """write page to text file"""
        self.write_logfile(soup, False)
        elements_searched = ["p"]
        self.handle_duplicate_pages(soup, rec_depth, elements_searched)

    def handle_duplicate_pages(self, soup, rec_depth, elements_searched):
        try:
            if not os.path.isfile("raw_output/" +
            self.symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_") + '.txt'):
                self.write_page_text(soup, rec_depth, elements_searched)
        except FileExistsError:
            logger.info("Attempted to write duplicate page.")

    def write_page_text(self, soup, rec_depth, elements_searched):
        with open( "raw_output/" +
            self.symbol_free_url + " " + datetime.now().strftime(
                "%Y-%m-%d_") + '.txt', 'x', encoding="utf-8") as output:
            for element in elements_searched:
                if len(soup.find_all(element)) > 0:
                    for paragraph in soup.find_all(element):
                        para_text = paragraph.getText()
                        if len(para_text.split()) > 8: #filter by >8 words
                            try:
                                output.write(para_text + "\n")
                            #this shouldn't be needed
                            except UnicodeEncodeError:
                                logger.warning("handled unicode encode error, line 72")
                        else:
                            logger.debug("too short: " + para_text)
            self.recur(soup, rec_depth)
            output.close()

    def recur(self, soup, rec_depth):
        """recursive searching of linked pages"""
        rec_depth += 1
        parsed_uri = urlparse(self.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        logger.debug("domain = " + domain)

        def has_ignored_terms(text):
            return any(word in Scraped_Page.ignored_terms for word in text.split(" "))

        links_in_page = soup.find_all("a", href=True)
        if rec_depth <= 2 and len(links_in_page) > 0:
            filtered_links = [link for link in links_in_page if not has_ignored_terms(remove_symbols(link))]
            logger.debug("testing if link is eligible --> " + str(links_in_page))
            for link in filtered_links:
                self.url = link.get('href')
                symbol_free_url = remove_symbols(link)
                if not os.path.isfile(symbol_free_url + " " + datetime.now().strftime(
                        "%Y-%m-%d_") + '.txt'):
                    self.attempt_recursive_call(rec_depth, domain, link)

    def attempt_recursive_call(self, rec_depth, domain, link):
        try:
            logger.debug("rec_depth = " + str(rec_depth)+ "; processing " + self.url)
            process_page(rec_depth, link)
        except UnicodeEncodeError:
            logger.warning("handled unicode error, line 108")
        except TypeError:
            logger.warning("handled type error, line 110")
        except requests.exceptions.InvalidSchema:
            logger.warning("handled requests.exceptions.InvalidSchema, line 112")
        except requests.exceptions.MissingSchema:
            self.url = domain+link.get('href')
            self.symbol_free_url = remove_symbols(self.url)
            if not os.path.isfile(self.symbol_free_url + " " + datetime.now(
            ).strftime("%Y-%m-%d_") + '.txt'):
                logger.debug(
                    "rec_depth = " + str(rec_depth)+"; processing link w/o TLD "
                     + self.symbol_free_url)
                process_page(rec_depth, self.url)

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
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    this_session = requests.Session()

    #connection = aiohttp.BaseConnector(conn_timeout=10,limit=20)
    #this_session = aiohttp.ClientSession(connector=connection)

    route_requests(scrape_sources.COFFEE_PAGES)

    this_page.delete_irrelevant_texts()
