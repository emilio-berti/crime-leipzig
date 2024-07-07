import sys
import feedparser
import requests
from bs4 import BeautifulSoup
import re

feed = feedparser.parse("https://www.polizei.sachsen.de/de/presse_rss_pdl.xml")

entry = feed.entries[12]

def report(entry):
	# title
	title = entry.title
	report = requests.get(entry.link).text
	# place
	[start, end] = re.search('Ort: ', report).span()
	report = report[end:]
	[start, end] = re.search('<br', report).span()
	place = report[:start]
	place = place.replace("&szlig;", "ss")
	# timedate
	[start, end] = re.search('Zeit: ', report).span()
	report = report[end:]
	[start, end] = re.search('</p', report).span()
	date = report[:start]

	ans = {
		'title': title,
		'place': place,
		'data': date
	}
	return ans

report(feed.entries[12])