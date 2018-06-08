import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split



def get_all_lyrics_chords(song_dict):
    ''''
    From song_dict (parsed song in MongoDB collection),
    Returns list of chords and list of lyrics for one song.
    '''
    song_lyrics = ' '.join(song_dict['words'])
    song_chords = []
    for chord_idx in song_dict['chord_idxs']:
        song_chords.append(chord_idx[1])
    return (song_lyrics, song_chords)


def make_song_dicts(parsed_songs):
    '''
    Returns list of dictionaries: One dict for each song, containing the lyrics and the chords for that song.
    '''
    song_dict_list = []
    for song in parsed_songs:
        song_dict  = {}
        song_dict['lyrics'] = get_all_lyrics_chords(song)[0]
        song_dict['chords'] = get_all_lyrics_chords(song)[1]
        song_dict_list.append(song_dict)
    return song_dict_list


def make_lists(song_dict_list):
    '''
    For every song in in song_dict_list, returns the list of lyrics and a boolean indicating whether the song contains a minor key (True) or not (False).
    Lists returned have one element for each song.
    '''
    contains_minor_list = []
    lyrics_list = []
    for song_dict in song_dict_list:
        contains_minor_list.append(any('m' in chord for chord in song_dict['chords']))
        lyrics_list.append(song_dict['lyrics'])
    return lyrics_list, contains_minor_list


def make_df(lyrics_list, contains_minor_list):
    '''
    Creates dataframe with columns for the list of lyrics and the boolean indicating whether the song has a minor key or not. Dataframe has one row for each song.
    '''
    df = pd.DataFrame({'lyrics': lyrics_list,
                   'contains_minor': contains_minor_list
                   })
    return df


if __name__ == "__main__":

    # identify and initialize MongoDB database
    mc = pymongo.MongoClient()
    db = mc['chordify']

    # identify MongoDB collection
    parsed_songs_db = db["parsed_songs"]
    parsed_songs = list(parsed_songs_db.find())

    # create aliases for models
    tfidf = TfidfVectorizer()
    logistic = LogisticRegression()

    # call functions to build lists of lyrics, idenitfy songs with minor key, and create dateframe
    song_dict_list = make_song_dicts(parsed_songs)
    lyrics_list, contains_minor_list = make_lists(song_dict_list)
    df_logi_song = make_df(lyrics_list, contains_minor_list)

    # create test and train sets of lyrics (X) and contains_minor (y)
    lyrics_train, lyrics_test, contains_minor_train, contains_minor_test = train_test_split(df_logi_song['lyrics'], df_logi_song['contains_minor'])

    # fit and transform training lyrics (X_train) using Tf-idf vectorization
    tfidf.fit(lyrics_train)
    train_matrix = tfidf.transform(lyrics_train)

    # fit the logistic regression model on training data
    logistic.fit(train_matrix, contains_minor_train)

    # transform test lyrics (X_test) using Tf-idf vectorization
    test_matrix = tfidf.transform(lyrics_test)

    # make logistic regression predictions on test data 
    y_hat_log = logistic.predict_proba(test_matrix)
    contains_minor_pred = logistic.predict(test_matrix)
    log_score = logistic.score(test_matrix, contains_minor_test)
