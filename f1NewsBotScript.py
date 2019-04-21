import time
from lxml.html import fromstring	# Web scraping. Pull fromstring function from lxml
# import nltk							# Splits sentences for web scraping
# nltk.download('punkt')
import requests						# Web scraping 
from twitter import OAuth, Twitter  # Pull OAuth and twitter functions
import credentials 					# API keys file

# Object for splitting paragraphs - not in use in this version
# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# Authentication object. Feed OAuth class API keys. 
oauth = OAuth (
		credentials.ACCESS_TOKEN,
		credentials.ACCESS_SECRET,
		credentials.CONSUMER_KEY,
		credentials.CONSUMER_SECRET
	)
# Authenticate bot
t = Twitter(auth=oauth)
# Header to server will recognize bot as real client
HEADERS = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
              ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
}

# Function to scrape AutosportsF1
def autosportsf1Scraper():
    # Save webpge to variable dom. dom.content is equivalent to inspect. 
    url = 'https://www.autosport.com/f1'
    dom = requests.get(url, headers=HEADERS)
    # Construcst tree structure of webpage. 
    tree = fromstring(dom.content)
    # Access all div elements with a class of newsitem
    links = tree.xpath('//div[@class="newsitem"]//a/@href')
    # Remove unwanted entries
    linksCopy = []
    for i in links:
    	if i != '/f1':
    		linksCopy.append(i)
    links = linksCopy
    # Extract headlines
    for link in links:
    	newDom = requests.get('https://www.autosport.com' + link, headers=HEADERS)
    	newDomTree = fromstring(newDom.content)
    	newDomText = newDomTree.xpath('//h1/text()')
    	newDomText = newDomText[0]
    	if not newDomText:
    		continue
    	yield '%s %s' % (newDomText, 'https://www.autosport.com' + link)

def formula1Scraper():
	url = 'https://www.formula1.com/en/latest/all.html'
	dom = requests.get(url, headers=HEADERS)
	tree = fromstring(dom.content)
	links = tree.xpath('//div[@class="f1-latest-listing--grid-item col-12 col-md-6 col-lg-4"]//a/@href')
	for link in links:
		newDom = requests.get('https://www.formula1.com' + link, headers=HEADERS)
		newDomTree = fromstring(newDom.content)
		newDomText = newDomTree.xpath('//h1[@class="f1--xl"]/text()')
		newDomText = newDomText[0]
		if not newDomText:
			continue
		yield '%s %s' % (newDomText, 'https://www.formula1.com' + link)

def raceFansScraper():
	url = 'https://www.racefans.net/'
	dom = requests.get(url, headers=HEADERS)
	tree = fromstring(dom.content)
	links = tree.xpath('//a[@class="post-thumbnail-homepage"]/@href')
	for link in links:
		newDom = requests.get(link, headers=HEADERS)
		newDomTree = fromstring(newDom.content)
		newDomText = newDomTree.xpath('//h1[@class="entry-title"]/text()')
		newDomText = newDomText[0]
		if not newDomText:
			continue
		yield '%s %s' % (newDomText, 'https://www.formula1.com' + link)

def main():
	print('--------------------START BOT--------------------')
	scraperNames = ['autosportsf1Scraper', 'formula1Scraper', 'raceFansScraper']
	scraperFunctions = []
	for name in scraperNames:
		scraperFunctions.append(globals()[name]())
	index = 0

	while True:
		currentScraper = scraperFunctions[index]
		try:
			tweet = next(currentScraper)
			print(tweet, end='\n\n')
			t.statuses.update(status=tweet)
			time.sleep(60)
		except StopIteration:
			print('StopIteration hit', end='\n\n')
			index += 1
			if index > len(scraperNames) - 1:
				index = 0
			time.sleep(60)
		except:
			print('Error hit')
			time.sleep(60)

if __name__ == "__main__":
	main()