import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# from src.logistic_by_line import tfidf, logistic

import src.logistic_by_line

class LogisticLyricAnalyzer:

    def __init__(self, tfidf, logistic):

        self.tfidf = tfidf
        self.logistic = logistic

    def predict(self, words):

        self.words = words
        self.tfidf.fit(words)
        X = self.tfidf.transform(words)

        is_minor_pred = self.logistic.predict_proba(X)

        return is_minor_pred
