browser = Chrome()

db = mc['chordify']
raw_html = db['raw_html']

def make_urls(n):
    '''get list of page urls for given artist'''
    artist_urls = []
    for num in range(n+1):
        artist_urls.append('https://www.ultimate-guitar.com/artist/bob_dylan_10212?filter=chords&page='
                    + str(num))
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

def scrape_songs(song_urls):
    '''scrape each song link into MongoDB'''
    for song_url in song_urls:
        song_html = scrape_song_page(song_url)
        print (song_html)
        raw_html.insert_one (
            {'url': url,
             'datetime': datetime.datetime.now(),
             'song_html': song_html
            })

def scrape_song_page(song_url):
    '''get raw song html from page'''
    browser.get(song_url)
    time.sleep(5)
    song_html = browser.page_source
    return song_html
