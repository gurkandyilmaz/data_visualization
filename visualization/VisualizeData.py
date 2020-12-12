import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from nltk import FreqDist, word_tokenize, RegexpTokenizer, stem
from snowballstemmer import TurkishStemmer

import time
from string import punctuation
from pathlib import Path



class VisualizeData():
    def __init__(self, images_dir_to_save):
        self._images_dir = images_dir_to_save

    def plot_counts_vs_word(self, frequencies_by_column):
        for column_name in frequencies_by_column.keys():
            title = "Word Counts by " + column_name
            plt.figure(figsize=(20,8))
            plt.ion()
            plt.title(title)
            plt.ylabel("Counts")
            plt.xticks(rotation=90)
            plt.bar(frequencies_by_column[column_name].keys(), frequencies_by_column[column_name].values())
            image_file = Path.joinpath(self._images_dir, "{title}.png".format(title=title))
            plt.ioff()
            plt.savefig(image_file, bbox_inches="tight")
        
    def plot_wordcloud(self, frequencies_by_column):
        for column_name in frequencies_by_column.keys():
            word_cloud = WordCloud(background_color="white", width=1200, height=400).generate_from_frequencies(frequencies_by_column[column_name])
            image_file = Path.joinpath(self._images_dir, "WordCloud by {name}.png".format(name=column_name))
            plt.figure(figsize=(20,8))
            plt.imshow(word_cloud, interpolation="bilinear")
            plt.axis("off")
            plt.ioff()
            word_cloud.to_file(image_file)
    
    def plot_row_length(self, df_with_row_length):
        for name in df_with_row_length.columns.to_list():
            title = "Row Length in " + name
            plt.figure(figsize=(20,8))
            plt.title(title)
            plt.ylabel("Count")
            plt.xlabel("Row Length")
            plt.hist(df_with_row_length[name])
            image_file = Path.joinpath(self._images_dir, "{title}.png".format(title=title))
            plt.savefig(image_file, bbox_inches="tight")
            plt.ioff()

    def plot_correlation(self, correlation_matrix):
        title = "Correlation Matrix"
        plt.figure(figsize=(20,8))
        plt.title(title)
        sns.heatmap(correlation_matrix, annot=True)
        image_file = Path.joinpath(self._images_dir, "{title}.png".format(title=title))
        plt.savefig(image_file, bbox_inches="tight")
        plt.ioff()
    
    def plot_hist(self, df_numeric):
        for name in df_numeric.columns.to_list():
            plt.figure(figsize=(20,8))
            plt.title(name)
            plt.ylabel("Frequency")
            plt.xlabel("(bins=50)")
            plt.hist(df_numeric[name], bins=50)
            name = name.replace("/", " ")
            image_file = Path.joinpath(self._images_dir, "{name}.png".format(name=name))
            plt.savefig(image_file, bbox_inches="tight")
            plt.ioff()
        
        
        