from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pymongo
import datetime
import time

mc = pymongo.MongoClient()

browser = Chrome()

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

def make_urls(base_url, n=12):
    '''get list of page urls for given artist'''
    artist_urls = []
    for num in range(n+1):
        artist_urls.append(base_url + str(num))
    return artist_urls


def get_all_urls(artist_urls):
    '''iterate through n pages for artist'''
    for artist_url in artist_urls:
        song_urls = get_song_urls(artist_url)
    return song_urls


def get_song_urls(artist_url):
    '''get urls to song pages'''
    browser.get(artist_url)
    time.sleep(2)
    song_block = soup.select('article.YMhU9 a')
    song_urls = [s.attrs.get('href') for s in song_block]
    return song_urls


def scrape_song_page(song_url):
    '''get raw song html from page'''
    browser.get(song_url)
    time.sleep(5)
    html = browser.page_source
    return html


def scrape_songs(song_urls):
    '''scrape each song link into MongoDB'''


if __name__ == "__main__":


    mc = pymongo.MongoClient()
    db = mc['chordify']
    raw_html = db['raw_html']

    base_url = 'https://www.ultimate-guitar.com/artist/bob_dylan_10212?filter=chords&page='
    artist_urls = make_urls(base_url, n=12)
    song_urls = get_all_urls(artist_urls)

    for song_url in song_urls:
        html = scrape_song_page(song_url)
        print (html)
        raw_html.insert_one (
            {'url': url,
             'datetime': datetime.datetime.now(),
             'html': html
            })
