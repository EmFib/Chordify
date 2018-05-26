# Chordify

### Chord predictions based on user lyrics

For much of rock, pop, folk, and other types of music, the key and the chord choices throughout out the song serve to amplify the message coming out of the lyrics. As a musician and aspiring song writer, I've had trouble composing music after writing lyrics.

Chordify addresses this issue for beginning songwriters! 

Chordify is a user interface that allows songwriters to input English words and receive suggested chords based on those words to use as the songwriter begins to compose a song. The chord suggestions reflect a preponderance of word-chord associations represented in the 8,000-song sample set.  A user can receive chord recommendations for a long piece of text or line-by-line recommendations for chord changes. The chords will inspire the songwriter and provide a foundation upon which a custom song can be composed. 

### Data scraping and parsing 

8,000 songs were scraped from https://www.ultimate-guitar.com/ and parsed into separate lines of words and chords, with each chord matched to the word it landed on via character indexing. From there, I pulled out the 10 words that surrounded the chord (seven before and three after) and made chord-word association for each of those 10 words.  

### Modeling 
