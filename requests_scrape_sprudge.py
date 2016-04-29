"""Scraping sprudge-linked coffee sites"""
import os, os.path, re, requests, logging, scrape_sources
from datetime import datetime
from string import printable
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class Options():
    url = ""
    symbol_free_url = ""
    session = None
    ignored_terms = ["twitter", "facebook", "google", "instagram", "apple", "pinterest",
                     "youtube", "account", "login", "register",
                     "cart", "about", "contact", "wholesale", "blog", "careers",
                     "learn", "location", "locations", "tea", "education", "squareup"]

def route_requests(url_list, rec_depth=0):
    """Let's get shit started"""
    Options.session = requests.Session()
    for url in url_list:
        Options.url = url
        parse_html_and_write(rec_depth)

def parse_html_and_write(rec_depth):
    content = return_html(Options.url)
    Options.symbol_free_url = remove_symbols(Options.url)
    logger.info("symbol_free_url= " + Options.symbol_free_url)
    soup = BeautifulSoup(content, "html.parser")
    prepare_page(soup, rec_depth)

def return_html(url):
    """print html of a given URL"""
    source_html = (Options.session.get(url)).text
    content = ''.join([x for x in source_html if x in printable and not x.isdigit()])
    return content

def prepare_page(soup, rec_depth):
    """write page to text file"""
    write_logfile(soup, False)
    elements_searched = ["p"]
    handle_duplicate_pages(soup, rec_depth, elements_searched)

def handle_duplicate_pages(soup, rec_depth, elements_searched):
    try:
        if not os.path.isfile("raw_output/" +
        Options.symbol_free_url + " " + datetime.now().strftime(
            "%Y-%m-%d_") + '.txt'):
            write_page_text(soup, rec_depth, elements_searched)
    except FileExistsError:
        logger.info("Attempted to write duplicate page.")

def write_page_text(soup, rec_depth, elements_searched):
    with open( "raw_output/" +
        Options.symbol_free_url + " " + datetime.now().strftime(
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
        recur(soup, rec_depth)
        output.close()

def recur(soup, rec_depth):
    """recursive searching of linked pages
    TODO: separate this function and refactor"""
    rec_depth += 1
    parsed_uri = urlparse(Options.url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    logger.info("domain = " + domain)

    def has_ignored_terms(text):
        return any(word in Options.ignored_terms for word in text.split(" "))

    links_in_page = soup.find_all("a", href=True)
    if rec_depth <= 2 and len(links_in_page) > 0:
        filtered_links = [link for link in links_in_page if not has_ignored_terms(remove_symbols(link))]
        for link in filtered_links:
            Options.url = link.get('href')
            symbol_free_url = remove_symbols(link)
            if not os.path.isfile(symbol_free_url + " " + datetime.now().strftime(
                    "%Y-%m-%d_") + '.txt'):
                attempt_recursive_call(rec_depth, domain, link)

def remove_symbols(url):
    """remove symbols from a URL"""
    return re.sub(r'[^\w]', ' ', Options.url)

def attempt_recursive_call(rec_depth, domain, link):
    try:
        logger.info("rec_depth = " + str(rec_depth)+ "; processing " + Options.url)
        parse_html_and_write(rec_depth)
    except UnicodeEncodeError:
        logger.warning("handled unicode error, line 108")
    except TypeError:
        logger.warning("handled type error, line 110")
    except requests.exceptions.InvalidSchema:
        logger.warning("handled requests.exceptions.InvalidSchema, line 112")
    except requests.exceptions.MissingSchema:
        Options.url = domain+link.get('href')
        Options.symbol_free_url = remove_symbols(Options.url)
        if not os.path.isfile(Options.symbol_free_url + " " + datetime.now(
        ).strftime("%Y-%m-%d_") + '.txt'):
            logger.info(
                "rec_depth = " + str(rec_depth)+"; processing link w/o TLD " + Options.symbol_free_url)
            parse_html_and_write(rec_depth)

def log_links_on_page(soup):
    """print links on page to log file"""
    with open("LINKS: " + Options.symbol_free_url + " " + datetime.now().strftime(
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
        with open("raw_output/" +
            "SCRAPE_LOG" + " " + datetime.now().strftime(
                "%Y-%m-%d") + '.txt', 'a') as logfile:
            logfile.write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            logfile.write("\n" + str(soup.title) + "\n" + "\n")
            logfile.close()




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    route_requests(scrape_sources.COFFEE_PAGES)
