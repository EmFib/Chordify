import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


from src.logistic_many_chords import *

chord_list = ['A','B','C','D','E','F','G','A7','D7','Em','Am','Bm','Dm','Bb']


class LogisticChordAnalyzer:

    def __init__(self, tfidf, logistic, chord_list, chord_model_dict, chord_prob_dict):

        self.tfidf = tfidf
        self.logistic = logistic
        self.chord_list = chord_list
        self.chord_model_dict = chord_model_dict
        self.chord_prob_dict = chord_prob_dict


    def fit(self, df_train):

        self.tfidf = TfidfVectorizer()
        X_train = df_train['words']
        self.tfidf.fit(X_train)

        for chord in chord_list:

            logistic = LogisticRegression()
            y_train = df_train[chord]
            tr_matrix = self.tfidf.transform(X_train)
            logistic.fit(tr_matrix, y_train)
            self.chord_model_dict[chord] = logistic

    def predict(self, some_words):

        words = [some_words]
        X = self.tfidf.transform(words)

        chord_prob_dict = {}

        for chord in chords_list:

            chord_prob_dict[chord] = self.chord_model_dict[chord].predict_proba(X)

        best_chord = max(chord_prob_dict.items(), key=lambda k: k[1])

        return best_chord

if __name__ == "__main__":

    logistic.fit(df_train)
    logistic.predict(some_words)

    some_words = 'beautiful terrible thunderstorm trucks mama heartbreak love kill find chase'
