import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split


def get_all_lyrics_chords(song_dict):
    song_lyrics = ' '.join(song_dict['words'])
    song_chords = []
    for chord_idx in song_dict['chord_idxs']:
        song_chords.append(chord_idx[1])
    return (song_lyrics, song_chords)


def make_song_dicts(parsed_songs):
    song_dict_list = []
    for song in parsed_songs:
        song_dict  = {}
        song_dict['lyrics'] = get_all_lyrics_chords(song)[0]
        song_dict['chords'] = get_all_lyrics_chords(song)[1]
        song_dict_list.append(song_dict)
    return song_dict_list


def make_lists(song_dict_list):
    contains_minor_list = []
    lyrics_list = []
    for song_dict in song_dict_list:
        contains_minor_list.append(any('m' in chord for chord in song_dict['chords']))
        lyrics_list.append(song_dict['lyrics'])
    return lyrics_list, contains_minor_list


def make_df(lyrics_list, contains_minor_list):
    df = pd.DataFrame({'lyrics': lyrics_list,
                   'contains_minor': contains_minor_list
                   })
    return df


if __name__ == "__main__":

    mc = pymongo.MongoClient()
    db = mc['chordify']

    parsed_songs_db = db["parsed_songs"]
    parsed_songs = list(parsed_songs_db.find())

    tfidf = TfidfVectorizer()
    nb = MultinomialNB()

    song_dict_list = make_song_dicts(parsed_songs)
    lyrics_list, contains_minor_list = make_lists(song_dict_list)
    df = make_df(lyrics_list, contains_minor_list)

    lyrics_train, lyrics_test, contains_minor_train, contains_minor_test = train_test_split(df['lyrics'], df['contains_minor'])

    tfidf.fit(lyrics_train)
    train_matrix = tfidf.transform(lyrics_train)

    nb.fit(train_matrix, contains_minor_train)

    test_matrix = tfidf.transform(lyrics_test)
    y_hat_nb = nb.predict_proba(test_matrix)
    nb_score = nb.score(test_matrix, contains_minor_test)
