Coffee Sites Scraper + Markov Generator
=========================
Currently, this has two main components.

First, `async_scrape.py` scrapes a bunch of roasted coffee pages, mostly
of Sprudge sponsors but also a few others since I wanted a large dictionary size
for Markov generation. (If you want a better option, try Scrapy.)  

It's now asynchronous and runs in ~5-6 minutes as opposed to 30-40 minutes previously.

The second part is taken pretty much verbatim from `https://github.com/hrs/markov-sentence-generator`. I lightly modified the code to be compatible with Python 3.x

The last part is some straight-forward analysis. The `nltk_analysis.py` file includes a few straight-forward analyses based on the natural language toolkit that don't reveal much. `sentiment_analysis_coffee` includes basic naive analysis of the text for positive and negative emotional valence words. Unsurprisingly, coffee sites tend to emphasize positive terms in describing their coffees. If you wanted to make these analyses more interesting, you could start doing comparative analyses between different sites/vendors.

You can use the raw scrape data in `/markov/` for your own fun :)

