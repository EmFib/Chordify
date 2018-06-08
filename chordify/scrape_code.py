from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pymongo
import datetime
import time
import random
import boto3

s3 = boto3.client('s3')

mc = pymongo.MongoClient()
db = mc['chordify']
raw_html = db['raw_html']

browser = Chrome()


# https://www.ultimate-guitar.com/explore?capo[]=0&genres[]=666&page=2&part[]=&tuning[]=1&type[]=Chords
# https://www.ultimate-guitar.com/explore?decade[]=1990&order=hitstotal_desc&page=2&type[]=Chords

# https://www.ultimate-guitar.com/explore?order=rating_desc&page=2&type[]=Chords

base_url = 'https://www.ultimate-guitar.com/explore?order=rating_desc&page='
base_url_2 = '&type[]=Chords'

def make_urls(base_url, base_url_2, n=500):
    '''get list of urls for given artist or genre'''
    artist_urls = []
    for num in range(1, n+1):
        artist_urls.append(base_url + str(num) + base_url_2)
        # artist_urls.append(base_url + str(num))
    return artist_urls


def get_all_urls(artist_urls):
    '''iterate through n pages for artist'''
    for artist_url in artist_urls:
        yield from(get_song_urls(artist_url))


def get_song_urls(artist_url):
    '''returns urls to song pages'''
    print (artist_url)
    browser.get(artist_url)
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    song_block = soup.select('article.YMhU9 a')
    song_urls = [s.attrs.get('href') for s in song_block]
    return song_urls


def scrape_song_page(song_url, retrieve_from_cache=True):
    '''get raw song html from page'''
    if retrieve_from_cache:
        result = retrieve_song(song_url)
        if result:
            if 'html' in result:
                return result['html']
            if 'song_html' in result:
                return result['song_html']
    browser.get(song_url)
    time.sleep(5)
    html = browser.page_source
    return html


def retrieve_song(song_url):
    '''to avoid duplicates,
    looks for the html in the collection'''
    result = raw_html.find_one({'url': song_url})
    return result


def scrape_songs(song_urls):
    '''puts each song html into MongoDB collection
    (if not a duplicate)'''

    for song_url in song_urls:
        print (song_url)
        html = scrape_song_page(song_url)
        if retrieve_song(song_url) is None:
            raw_html.insert_one (
                {'url': song_url,
                 'datetime': datetime.datetime.now(),
                 'html': html
                })


def main():
    artist_urls = make_urls(base_url, base_url_2, n=500)
    song_urls = get_all_urls(artist_urls)
    # song_urls = get_song_urls(artist_url)
    scrape_songs(song_urls)


if __name__ == "__main__":
    main()
