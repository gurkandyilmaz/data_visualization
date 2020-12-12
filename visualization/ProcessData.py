
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from nltk import FreqDist, word_tokenize, RegexpTokenizer, stem
from snowballstemmer import TurkishStemmer

import time
from string import punctuation
from pathlib import Path


class ProcessData():
    def __init__(self):
        print("Class INITIATED with cwd: {}".format(Path.cwd()))
        self._stopwords_tr = self.read_stopwords(Path.cwd().parent.joinpath("visualization/data/stopwords_tr.txt"))
        self._stopwords_en = self.read_stopwords(Path.cwd().parent.joinpath("visualization/data/stopwords_en.txt"))
        self._stemmer_en = stem.SnowballStemmer('english')
        self._stemmer_tr = TurkishStemmer()

    def read_file(self, excel_file_path):
        # excel_file_path = Path.joinpath(Path.cwd(), "data").joinpath(excel_filename)
        try:
            t0 = time.time()
            df = pd.read_excel(excel_file_path)
            print("File {0} Read Time: {1:.5f} sec.".format(excel_file_path, time.time() - t0))
            return df
        except Exception as e:
            print(e)

    def process_df_text(self, df):
        df_text = df.select_dtypes(include=["object"]).copy()
        # df_text.fillna("NULL", inplace=True)
        df_text.dropna(inplace=True)
        text_series = df_text.apply(lambda text: " ".join(text.values))
        text_series = text_series.apply(self.make_lowercase)
        text_series = text_series.apply(self.remove_puncts)
        text_series = text_series.apply(self.remove_stopwords)
        text_series = text_series.apply(self.remove_numbers)
        text_series = text_series.apply(self.stem_words)

        df_row_length = df_text.apply(self.row_length)

        return text_series, df_row_length

    def process_df_numeric(self, df):
        df_numeric = df.select_dtypes(include=["number"])
        corr_matrix = df_numeric.corr()
        return df_numeric, corr_matrix
    
    def make_lowercase(self, text):
        return text.lower()
    
    def remove_puncts(self, text):
        return text.translate(text.maketrans("", "", punctuation))
    
    def remove_stopwords(self, text, language="turkish"):
        tokens = self.tokenize_text(text)
        if language == 'turkish':
            stopwords = self._stopwords_tr
        elif language == 'english':
            stopwords = self._stopwords_en
        stopwords_removed = " ".join([token for token in tokens if token not in stopwords])
        return stopwords_removed
    
    def remove_numbers(self, text):
        regex = RegexpTokenizer(r'[^\d\s\n]+')
        numbers_removed = " ".join(regex.tokenize(text))
        return numbers_removed

    def stem_words(self, text, language="turkish"):
        tokens = self.tokenize_text(text)
        if language == "turkish":
            stemmed_text = " ".join(self._stemmer_tr.stemWords(tokens))
        elif language == "english":
            stemmed_text = " ".join([self._stemmer_en.stem(token) for token in tokens])
        return stemmed_text
    
    def tokenize_text(self, text):
        return word_tokenize(text)
        
    def read_stopwords(self, stopwords_file):
        with open(stopwords_file, encoding="utf-8") as stopwords:
            stopwords_list = stopwords.readlines()
        stopwords_list = [stopword.strip() for stopword in stopwords_list]
        return stopwords_list

    def freq_dist(self, text):
        counter = CountVectorizer(ngram_range=(1,2), max_features=100)
        counter_fit = counter.fit_transform([text])
        counts = np.asarray(counter_fit.sum(axis=0))
        words = counter.get_feature_names()
        freq = {}
        for word, count in zip(words, counts[0]):
            freq[word] = count
        freq_sorted = {word:count for word,count in sorted(freq.items(), key=lambda item: item[1], reverse=True)}
        return freq_sorted

    def row_length(self, list_of_text):
        row_len = list()
        for element in list_of_text:
            row_len.append(len(element))
        return row_len