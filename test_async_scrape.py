"""tests implemented w/ pytest (http://pytest.org/)
run w/ e.g. py.test from this folder"""

import logging

import pytest
import grequests

import async_scrape

class TestGetDomain:
    """unittests; TODO"""
    def test_get_domain(self):
        logging.basicConfig(level=logging.CRITICAL)
        logger = logging.getLogger(__name__)
        assert async_scrape.get_domain(
            "http://pytest.org/latest/getting-started.html") == "http://pytest.org/"

class TestURLInclDomain:
    def test_includes_domain(self):
        assert async_scrape.url_includes_domain(
            "http://pytest.org/latest/getting-started.html") == True

    def test_doesnt_include_domain(self):
        assert async_scrape.url_includes_domain(
            "/pages/products/coffee_one") == False
        assert async_scrape.url_includes_domain(
            "/page/") == False

class TestRemoveSymbols:
    def test_remove_symbols_from_url(self):
        assert async_scrape.remove_symbols(
            "http://pytest.org/latest/getting-started.html") == "http   pytest org latest getting started html"
    def test_remove_symbols_strings(self):
        assert async_scrape.remove_symbols(
            "__360noscope&hello😆.") == "     noscope hello  "

class TestInitializePageObject:
    def test_initalized_values(self):
        assert this_page.url == ""
        assert this_page.symbol_free_url == ""
        assert this_page.content == ""
        assert this_page.timestamp == ""
        assert this_page.links_in_page == set()
        assert this_page.elements_searched == ["p"]
