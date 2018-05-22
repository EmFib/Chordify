import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def get_phrase_for_chord(one_parsed_song):
    '''
    Takes: parsed song as stored in MongoDB collection.
    Returns: a tuple for every chord change in the song. Tuple contains the chord, a phrase (string of words) representing the 7 words before and 3 words after the chord change, and the song id.
    '''
    song_id = str(one_parsed_song['_id'])
    word_list = one_parsed_song['words']
    one_song_chord_phrase_tuples = []

    for chord_set in one_parsed_song['chord_idxs']:
        word_idx = chord_set[0]
        chord_name = chord_set[1]
        phrase = ' '.join(word_list[(word_idx - 8):(word_idx + 3)])
        one_song_chord_phrase_tuples.append((chord_name, phrase, song_id))

    return one_song_chord_phrase_tuples


def get_all_phrase_chord_tuples(parsed_songs):
    '''
    Returns chord-phrase-song id tuples for every song in parsed songs.
    '''
    chord_phrase_tuples = []

    for song in parsed_songs:
        one_song_chord_phrase_tuples = get_phrase_for_chord(song)
        chord_phrase_tuples.extend(one_song_chord_phrase_tuples)

    return chord_phrase_tuples


def make_phrase_is_minor_list(chord_phrase_tuples):
    '''
    Creates lists of phrases, actual chords, whether chord is minor, and song id for song containing phrase. (All lists equal length.)
    '''
    phrases = []
    chords = []
    is_minor = []
    song_ids = []

    for chord_phrase_tup in chord_phrase_tuples:
        phrases.append(chord_phrase_tup[1])
        chords.append(chord_phrase_tup[0])
        is_minor.append('m' in chord_phrase_tup[0])
        song_ids.append(chord_phrase_tup[2])

    return phrases, chords, is_minor, song_ids


chord_list = ['A','B','C','D','E','F','G','G#','A7','D7','Em','Am','Bm','Dm','Bb']

def get_list_of_chords(chord_phrase_tuples):
    '''
    Each list represent a boolean identification for each chord in list of tuples -- True if the chord is said chord, False if not.
    '''
    is_A = []
    is_B = []
    is_C = []
    is_D = []
    is_E = []
    is_F = []
    is_G = []
    is_A7 = []
    is_D7 = []
    is_Em = []
    is_Am = []
    is_Bm = []
    is_Dm = []
    is_Bb = []
    other_chord = []
    for tup in chord_phrase_tuples:
        is_A.append(tup[0] == 'A')
        is_B.append(tup[0] == 'B')
        is_C.append(tup[0] == 'C')
        is_D.append(tup[0] == 'D')
        is_E.append(tup[0] == 'E')
        is_F.append(tup[0] == 'F')
        is_G.append(tup[0] == 'G' or tup[0] == 'G#')
        is_A7.append(tup[0] == 'A7')
        is_D7.append(tup[0] == 'D7')
        is_Em.append(tup[0] == 'Em')
        is_Am.append(tup[0] == 'Am')
        is_Bm.append(tup[0] == 'Bm')
        is_Dm.append(tup[0] == 'Dm')
        is_Bb.append(tup[0] == 'Bb')
        other_chord.append(tup[0] not in chord_list)
    return is_A, is_B, is_C, is_D, is_E, is_F, is_G, is_A7, is_D7, is_Em, is_Am, is_Bm, is_Bb, is_Dm, other_chord


def make_phrase_chord_df(chord_phrase_tuples):
    '''
    Creates dataframe with a row for every chord change in the songs provided. Has the following columns:
    - chord: chord entry for every chord change
    - words: words surroung chord change
    - song_id: id for song containing chord change + words
    - column for each chord: boolean indicating whether the chord change is that chord

    '''
    phrases, chords, is_minor, song_ids = make_phrase_is_minor_list(chord_phrase_tuples)

    is_A, is_B, is_C, is_D, is_E, is_F, is_G, is_A7, is_D7, is_Em, is_Am, is_Bm, is_Bb, is_Dm, other_chord = get_list_of_chords(chord_phrase_tuples)

    df = pd.DataFrame({
        'song_id': song_ids,
        'chord': chords,
        'A': is_A,
        'B': is_B,
        'C': is_C,
        'D': is_D,
        'E': is_E,
        'F': is_F,
        'G': is_G,
        'A7': is_A7,
        'D7': is_D7,
        'Em': is_Em,
        'Am': is_Am,
        'Bm': is_Bm,
        'Dm': is_Dm,
        'Bb': is_Bb,
        'other_chord': other_chord,
        'is_minor': is_minor,
        'words': phrases
    })

    return df

def get_data():

    # identify and initialize MongoDB database
    mc = pymongo.MongoClient()
    db = mc['chordify']

    # identify MongoDB collection
    parsed_songs_db = db["parsed_songs"]
    parsed_songs = list(parsed_songs_db.find())

    # create aliases for models
    tfidf = TfidfVectorizer()
    logistic = LogisticRegression()

    # call functions to build chord-phrase associations and turn into dataframe
    chord_phrase_tuples = get_all_phrase_chord_tuples(parsed_songs)
    df_chords = make_phrase_chord_df(chord_phrase_tuples)

    # create train and test dataframes ensuring that lines from same song do not enter both train and test sets
    tr, te = train_test_split(list(set(df_chords['song_id'])))
    df_train = df_chords[df_chords.song_id.isin(tr)]
    df_test = df_chords[df_chords.song_id.isin(te)]

    # return dataframes for use in other scripts
    return df_train, df_test
