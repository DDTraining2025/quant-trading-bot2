import feedparser

def fetch_rss_entries(feed_urls):
    entries = []
    for url in feed_urls:
        parsed = feedparser.parse(url)
        entries.extend(parsed.entries)
    return entries

feed_urls = [
    "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml",
    "https://www.prnewswire.com/rss/technology-latest-news.rss"
]
