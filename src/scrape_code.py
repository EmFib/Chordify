from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pymongo
import datetime
import time
import random


mc = pymongo.MongoClient()
db = mc['chordify']
raw_html = db['raw_html']

browser = Chrome()


base_url = 'https://www.ultimate-guitar.com/artist/paul_simon_11328?filter=chords&page='


def make_urls(base_url, n=4):
    '''get list of page urls for given artist'''
    artist_urls = []
    for num in range(n+1):
        artist_urls.append(base_url + str(num))
    return artist_urls


def get_all_urls(artist_urls):
    '''iterate through n pages for artist'''
    for artist_url in artist_urls:
        yield from(get_song_urls(artist_url))


def get_song_urls(artist_url):
    '''get urls to song pages'''
    print (artist_url)
    browser.get(artist_url)
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    song_block = soup.select('article.YMhU9 a')
    song_urls = [s.attrs.get('href') for s in song_block]
    return song_urls


def scrape_song_page(song_url):
    '''get raw song html from page'''
    browser.get(song_url)
    time.sleep(5)
    html = browser.page_source
    return html

## ADD retrieve song function
# if result none, go to url
# else continue

def scrape_songs(song_urls):
    '''scrape each song link into MongoDB'''

    for song_url in song_urls:
        print (song_url)
        html = scrape_song_page(song_url)
        raw_html.insert_one (
            {'url': song_url,
             'datetime': datetime.datetime.now(),
             'html': html
            })


def main():
    artist_urls = make_urls(base_url, n=9)
    song_urls = get_all_urls(artist_urls)
    scrape_songs(song_urls)


if __name__ == "__main__":
    main()
