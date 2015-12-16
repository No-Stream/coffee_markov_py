Coffee Sites Scraper + Markov Generator
=========================
Currently, this has two main components.

First, requests_scrape_sprudge.py scrapes a bunch of roasted coffee pages, mostly
of Sprudge sponsors but also a few others since I wanted a large dictionary size
for Markov generation. The code is largely naive because I wanted to write something
mostly from scratch. (If you want a better option, try Scrapy.) I've optimized it
a bit to get it running at a decent speed and to filter out some irrelevant pages.
Please also note it would run dramatically faster if you reduced the recursion depth
(`rec_depth`) to 1.

The second part is taken pretty much verbatim from `https://github.com/hrs/markov-sentence-generator`. I lightly modified the code to
be compatible with Python 3.x and will be adding some caching functionality to speed
up repeated runs and allow this to be hosted on a Django server.

Note: I've included commented out code for multiprocessing. It runs dramatically
more quickly but does introduce occasional errors, largely outside of my ability
to control. (E.g. 429 "too many requests")

*List of sites that do not scrape properly:*
`barnine
kaldiscoffee
parlorcoffee
ptscoffee`