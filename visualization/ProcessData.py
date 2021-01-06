
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
from utils.paths import get_visualization_folder


class ProcessData():
    def __init__(self):
        # print("Class INITIATED with cwd: {}".format(Path.cwd()))
        self._stopwords_tr = self.read_stopwords(get_visualization_folder() / "data/stopwords_tr.txt")
        self._stopwords_en = self.read_stopwords(get_visualization_folder() / "data/stopwords_en.txt")
        self._stemmer_en = stem.SnowballStemmer('english')
        self._stemmer_tr = TurkishStemmer()

    def read_file(self, excel_file_path):
        try:
            # t0 = time.time()
            df = pd.read_excel(excel_file_path)
            # print("UPLOADED File {0} Read Time: {1:.5f} sec.".format(excel_file_path, time.time() - t0))
            return df
        except Exception as error:
            return error
    
    def cast_datatypes(self, dataframe, user_selected_types):
        types = user_selected_types.get("types")
        df_copy = dataframe.copy().dropna()
        for col_name, col_type in types.items():
            if col_type == "text":
                try:
                    df_copy.loc[:, col_name] = df_copy.loc[:, col_name].astype(dtype={col_name:"object"})
                except Exception as error:
                    raise TypeError("Could not convert {name} column to {dtype}. Detail: {err}".format(name=col_name, dtype=col_type, err=error))
            elif col_type == "categoric":
                try:
                    df_copy.loc[:, col_name] = df_copy.loc[:, col_name].astype(dtype={col_name:"category"})
                except Exception as error:
                    raise TypeError("Could not convert {name} column to {dtype}. Detail: {err}".format(name=col_name, dtype=col_type, err=error))
            elif col_type == "numeric":
                try:
                    df_copy.loc[:, col_name] = df_copy.loc[:, col_name].astype(dtype={col_name:"int64"})
                except Exception as error:
                    raise TypeError("Could not convert {name} column to {dtype}. Detail: {err}".format(name=col_name, dtype=col_type, err=error))
            elif col_type == "datetime":
                try:
                    df_copy.loc[:, col_name] = df_copy.loc[:, col_name].astype(dtype={col_name:"datetime64[s]"})
                except Exception as error:
                    raise TypeError("Could not convert {name} column to {dtype}. Detail: {err}".format(name=col_name, dtype=col_type, err=error))

        return df_copy

    def process_categorical(self, dataframe): 
        df_categoric = dataframe.select_dtypes(include=["category"]).copy()
        return df_categoric

    def process_numeric(self, dataframe):
        df_numeric = dataframe.select_dtypes(include=["number"]).copy()
        return df_numeric
    
    def process_datetime(self, dataframe):
        # datetime format should be "day/month/year".
        df_datetime = dataframe.select_dtypes(include=["datetime"]).copy()
        # if not df_datetime.columns.empty:
        #     df_datetime = df_datetime.apply(lambda column: column.dt.strftime("%d/%m/%Y"))
        # dataframe = dataframe.sort_values(by=list(date_time)[0])
        # df = df.sort_values(by="timestamp_converted")
        # dataframe = dataframe.set_index(list(date_time)[0])
        # df_datetime = df.select_dtypes(include=["datetime"])
        return df_datetime

    def process_text(self, dataframe):
        df_text = dataframe.select_dtypes(include=["object"]).copy()
        text_dict = df_text.apply(lambda text: " ".join(text.values)).to_dict()
        text_dict_processed = {}
        for label, text in text_dict.items():
            text = self.make_lowercase(text)
            text = self.remove_puncts(text)
            text = self.remove_stopwords(text)
            text = self.remove_numbers(text)
            # text = self.stem_words(text)
            text_dict_processed.update({label:text})

        return text_dict_processed

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

    # def freq_dist(self, text):
    #     counter = CountVectorizer(ngram_range=(1,2), max_features=100)
    #     counter_fit = counter.fit_transform([text])
    #     counts = np.asarray(counter_fit.sum(axis=0))
    #     words = counter.get_feature_names()
    #     freq = {}
    #     for word, count in zip(words, counts[0]):
    #         freq[word] = count
    #     freq_sorted = {word:count for word,count in sorted(freq.items(), key=lambda item: item[1], reverse=True)}
    #     return freq_sorted

    # def row_length(self, list_of_text):
    #     row_len = list()
    #     for element in list_of_text:
    #         row_len.append(len(element))
    #     return row_len
