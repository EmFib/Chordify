# Chordify

## Chord predictions based on user lyrics

### Motivation

For much of rock, pop, folk, and other types of music, the key and the chord choices throughout out the song serve to amplify the message coming out of the lyrics. As a musician and aspiring song writer, I've had trouble composing music after writing lyrics.

Chordify addresses this issue for beginning songwriters!

### Product

Chordify is a user interface that allows songwriters to input English words and receive suggested chords based on those words to use as the songwriter begins to compose a song. The chord suggestions reflect a preponderance of word-chord associations represented in the 8,000-song sample set.  A user can receive chord recommendations for a long piece of text or line-by-line recommendations for chord changes. The chords will inspire the songwriter and provide a foundation upon which a custom song can be composed.  

Chordify is a user interface that allows songwriters to input English words and receive suggested chords based on those words to use as the songwriter begins to compose a song. The chord suggestions reflect a preponderance of word-chord associations represented in the 8,000-song sample set.  A user can receive chord recommendations for a long piece of text or line-by-line recommendations for chord changes. The chords will inspire the songwriter and provide a foundation upon which a custom song can be composed.

### Data scraping and parsing

8,000 songs were scraped from [Ultimate-Guitar.com](https://www.ultimate-guitar.com/) and parsed into separate lines of words and chords, with each chord matched to the word it landed on via character indexing. From there, I pulled out the 10 words that surrounded the chord (seven before and three after) and made chord-word association for each of those 10 words.  

### Modeling

My model was based in Tf-Idf vectorization and Logistic Regression. The training dataframe included a row for each of the 10-word phrases I had pulled from the songs. The targets were boolean-columns for each of the 14 chords I chose to include, indicating whether that was the chord change associated with the phrase.

From there, I built a dictionary of 14 models - one for each of the chords. They each were transformed with Tf-Idf and fit with Logistic Regression.

For predictions, user-inputted words are transformed by the Tf-Idf vectorization and then a Logistic Regression predict_proba was ran for each of the models in the chord model dictionary. Chordify's chord prediction was the that which had the highest probability.

Example of relative probabilities for one line of text:

<!-- ![Feature Importance by Category](images/relative_chord_probabilities_slide.png) -->
<img align="center" src="images/relative_chord_probabilities_slide.png" width="600"/>

### Results 

I tested Chordify's chord predictions against actual chords shown on guitar sheet music for several songs. Below are sample results for Fleetwood Mac's "Landslide." The column in the middle represents Chordify's chord predictions while the far-right columns represents the chords on the sheet music. Highlighted in green are lines of lyrics where Chordify's prediction was accurate to the sheet music. 

<!-- ![Feature Importance by Category](images/landslide.png) -->
<img align="center" src="images/landslide.png" width="600"/>

The purpose of Chordify, however, is not to predict chords for songs that have already been written but to suggest chords based on words that are not yet set to music. I experimented with my favorite poem, Mary Oliver's _Wild Geese_. 

Note below how "love what it loves" is predicted to be a B minor. One interesting discovery thoughout my use cases was that Chordify linked the uncommon Bm chord to phrases including the word "love," which suggests that there is a prepondence of songs in the training dataset that associated Bm to the word. 

<!-- ![Feature Importance by Category](images/wild_geese.png) -->
<img align="center" src="images/wild_geese.png" width="600"/>

### Access the project

After cloning the repo, the following commands can be run in iPython:

###### Import the application

```import LogisticChordAnalyzer```

###### Run the main block

```LogisticChordAnalyzer.main()```

###### You will then be asked to enter words. No minimum or maximum number. Separate phrases with punctuation to (.,!?) to get separate  chord suggestion for different phrases.
