from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pymongo
import datetime
import time
import pandas as pd
import numpy as np
import re
import warnings
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import string
from src.parse import parse_many


def get_all_lyrics_chords(song):
    song_lyrics = ' '.join(song[1])
    song_chords = []
    for ch_tup in song[0]:
        song_chords.append(ch_tup[1])
    return (song_lyrics, song_chords)


def make_song_dicts(parsed_songs):
    song_dict_list = []
    for song in parsed_songs:
        song_dict  = {}
        song_dict['lyrics'] = get_all_lyrics_chords(song)[0]
        song_dict['chords'] = get_all_lyrics_chords(song)[1]
        song_dict_list.append(song_dict)
    return song_dict_list


def make_song_mats(song_dict_list):
    contains_minor_mat = []
    lyrics_mat = []
    for song_dict in song_dict_list:
        contains_minor_mat.append(any('m' in chord for chord in song_dict['chords']))
        lyrics_mat.append(song_dict['lyrics'])
    return lyrics_mat, contains_minor_mat

def make_df(lyrics_mat, contains_minor_mat):
    df = pd.DataFrame({'lyrics': lyrics_mat,
                   'contains_minor': contains_minor_mat
                   })
    return df

if __name__ == "__main__":

    mc = pymongo.MongoClient()
    db = mc['chordify']
    raw_html = db['raw_html']
    html_docs = list(raw_html.find())

    # tfidf = TfidfVectorizer()
    # logistic = LogisticRegression()

    parsed_songs = parse_many(html_docs[:5000])
    song_dict_list = make_song_dicts(parsed_songs)
    lyrics_mat, contains_minor_mat = make_song_mats(song_dict_list)

    df = make_df(lyrics_mat, contains_minor_mat)
