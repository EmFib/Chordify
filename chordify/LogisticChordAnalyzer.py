import pymongo
import string
import warnings
import re
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


from . import logistic_many_chords


chord_list = ['A','B','C','D','E','F','G','A7','D7','Em','Am','Bm','Dm','Bb']


class LogisticChordAnalyzer:
    '''
    Fits logistic regression model for each chord and gives most probably chord for user-inputted words.
    '''
    def __init__(self):
        self.chord_list = chord_list
        self.chord_model_dict = {}

    # fits logistic regression model for each chord in chord list and puts into dictionary
    def fit(self, df_train):
        self.tfidf = TfidfVectorizer()
        # self.logistic = LogisticRegression()
        X_train = df_train['words']
        self.tfidf.fit(X_train)
        for chord in chord_list:
            logistic = LogisticRegression()
            y_train = df_train[chord]
            tr_matrix = self.tfidf.transform(X_train)
            logistic.fit(tr_matrix, y_train)
            self.chord_model_dict[chord] = logistic

    # Takes user-input words and runs logistic regression for each chord in chord list. Puts predict_proba into diciontary; Returns chord and predict_proba for chord with highest probability.
    def predict(self, some_words):
        words = [some_words]
        X = self.tfidf.transform(words)
        chord_prob_dict = {}
        for chord in chord_list:
            chord_prob_dict[chord] = self.chord_model_dict[chord].predict_proba(X)[0][1]
        best_chord = max(chord_prob_dict.items(), key=lambda k: k[1])
        # print (chord_prob_dict)
        return best_chord


def fit_lca():
    '''
    Fits the LogisticChordAnalyzer on the entrie set of training data.
    '''
    df_train, df_test = logistic_many_chords.get_data()
    lca = LogisticChordAnalyzer()
    lca.fit(df_train)
    return lca


def get_words_and_lines():
    '''
    Gets words as user input and splits into lines by punctuation.
    '''
    while True:
        entry = input("Please enter your favorite words: ")
        if 3 <= len(entry.split()):
            lines = re.split('[?.,!-]', entry)
            return lines


def save_lca():
    '''
    Pickles trained logistic model so can be accessed more quickly.
    '''
    lca = fit_lca()
    with open('lca.pkl', 'wb') as f:
        pickle.dump(lca, f)


def load_lca():
    '''
    Retrieves trained logistic model.
    '''
    with open ('lca.pkl', 'rb') as f:
        lca = pickle.load(f)
    return lca


def main():
    lca = load_lca()
    lines = get_words_and_lines()
    for line in lines:
        if len(line) >= 2:
            best_line_chord = lca.predict(line)
            print ("{}:".format(line), best_line_chord)


    # *******
    # best_chord = lca.predict(some_words)
    # print (best_chord)
    # *******

if __name__ == "__main__":
    main()
