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
from nltk.corpus import stopwords

import nltk
import string
import numpy as np
import pandas as pd
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
nltk.download('stopwords')

from load_song_data import df


def clean_lyrics(doc):
    doc_no_stopwords = " ".join([i for i in doc.lower().split() if i not in stop_words])
    doc_no_punctuation = "".join(i for i in doc_no_stopwords if i not in punctuation)
    doc_Lemmatized = " ".join(lemmatize(i) for i in doc_no_punctuation.split())
    return doc

def create_bows(df):
    df['bow'] = df['lyrics'].apply(lambda x: clean_document(x))
    return df


def create_word_list(df, ):
    tfidf = TfidfVectorizer(stop_words='english',max_features=10000)

    tfidf.fit(df['bow'])
    lyrics_vectors = tfidf.transform(df['bow'])

    nb = MultinomialNB()

    nb.fit(lyrics_vectors, df['contains_minor'])

    y_hat = nb.predict_proba(lyrics_vectors)

    arr = np.argsort(nb.feature_log_prob_[0])[-20:-1]

    list_of_words = []

    for i in arr:
        list_of_words.append(tfidf.get_feature_names()[i])

    return list_of_words
