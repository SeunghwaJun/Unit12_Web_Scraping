
import pymongo
import requests
import numpy as np
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs

# DB Setup

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

# Scrape Data 

executable_path = {'executable_path': 'chromedriver.exe'}

def scrape():

	collection.drop()

	browser = Browser('chrome', **executable_path, headless=True)

	# NASA Mars News
	news_url ="https://mars.nasa.gov/news/"
	browser.visit(news_url)
	news_html = browser.html
	nsoup = bs(news_html,'lxml')
	news_title = nsoup.find('div', class_='content_title').text
	news_p = nsoup.find('div', class_='article_teaser_body').text


	# JPL Mars Space Images - Featured Image
	jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
	browser.visit(jpl_url)
	jpl_html = browser.html
	jsoup = bs(jpl_html,'lxml')
	img_link = jsoup.find('div',class_='carousel_container').article.footer.a['data-fancybox-href']
	base_link = jsoup.find('div', class_='jpl_logo').a['href'].rstrip('/')
	featured_image_title = jsoup.find('h1', class_="media_feature_title").text.strip()
	featured_image_url = base_link + img_link


	# Mars Weather
	weather_url = "https://twitter.com/marswxreport?lang=en"
	browser.visit(weather_url)
	weather_html = browser.html
	wsoup = bs(weather_html,'lxml')
	tweets = wsoup.find_all('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
	for tweet in tweets:
	    tweet_text = tweet.text
	    if tweet_text.startswith("InSight"):
	        mars_weather = tweet_text
	        break
	    else:
	        continue


	# Mars Facts
	fact_url = "http://space-facts.com/mars/"
	fact_table = pd.read_html(fact_url)
	mars_fact_table = fact_table[0]
	mars_fact_table_html = mars_fact_table.to_html(header=False, index=False)
	

	# Mars Hemispheres
	hem_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
	browser.visit(hem_url)
	urls = [(a.text, a['href']) for a in browser
	         .find_by_css('div[class="description"] a')]
	hemisphere_image_urls = []
	for title,url in urls:
	    product_dict = {}
	    product_dict['title'] = title
	    browser.visit(url)
	    img_url = browser.find_by_css('img[class="wide-image"]')['src']
	    product_dict['img_url'] = img_url
	    hemisphere_image_urls.append(product_dict)

	browser.quit()



	mars_data ={
		'news_title' : news_title,
		'summary': news_p,
		'featured_image': featured_image_url,
		'featured_image_title': featured_image_title,
		'weather': mars_weather,
		'fact_table': mars_fact_table_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jpl_url,
        'weather_url': weather_url,
        'fact_url': fact_url,
        'hemisphere_url': hem_url,
        }

	collection.insert(mars_data)

