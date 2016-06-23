import logging

import pytest
import grequests

import async_scrape

logger_ = logging.getLogger(__name__)
this_page_ = async_scrape.Scraped_Page()

@pytest.fixture(autouse=True)
def globals(request):
    request.function.__globals__['logger'] = logger_
    request.function.__globals__['this_page_'] = this_page_

@pytest.fixture(scope="session", autouse=True)
def init_():
    logging.basicConfig(level=logging.CRITICAL)
    print("Initialized testing session.")
