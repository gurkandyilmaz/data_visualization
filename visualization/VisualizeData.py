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
        self._figsize_x = 12
        self._figsize_y = 8
    
    def plot_bar(self, df_categoric, column):
        count = df_categoric.loc[:, column].value_counts()
        names = count.index.values
        values = count.values
        top_limit = 50   
        names_ticks = np.arange(len(names[:top_limit]))
        top_names = names[:top_limit]
        top_values = values[:top_limit]

        title = "Top {top_limit} {column} Counts".format(top_limit=top_limit, column=column)
        fig, ax = plt.subplots(figsize=(self._figsize_x, self._figsize_y))
        ax.bar(top_names, top_values)
        ax.set_ylabel('Counts')
        ax.set_title(title)
        ax.set_xticks(names_ticks)
        ax.set_xticklabels(top_names, rotation=90)

        # "\" or "/" characters caused an exception while saving
        column = column.replace("\\", " ").replace("/", " ")
        image_file = self._images_dir / "{column}_bar.png".format(column=column)
        fig.savefig(image_file, bbox_inches="tight")
    
    def plot_pie(self, df_categoric, column):
        df = df_categoric.copy()
        df.dropna(inplace=True)
        count = df.loc[:, column].value_counts()
        names = count.index.values
        values = count.values
        top_limit = 20   
        top_names = names[:top_limit]
        top_values = values[:top_limit]

        title = "Top {top_limit} {column} Ratio".format(top_limit=top_limit, column=column)
        fig, ax = plt.subplots(figsize=(self._figsize_x, self._figsize_y))
        ax.set_title(title)
        # fig.set_size_inches(figsize_x, figsize_y)
        wedges, texts, autotexts = ax.pie(top_values, autopct='%1.1f%%')
        ax.axis('equal')
        ax.legend(wedges, top_names, title="{0}".format(column), loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        column = column.replace("\\", " ").replace("/", " ")
        image_file = self._images_dir / "{column}_pie.png".format(column=column)
        fig.savefig(image_file, bbox_inches="tight")
        
    def plot_correlation(self, df_numeric):
        correlation_matrix = df_numeric.corr()
        title = "Correlation Matrix"
        plt.figure(figsize=(self._figsize_x, self._figsize_y))
        plt.title(title)
        sns.heatmap(correlation_matrix, annot=True)
        image_file = Path.joinpath(self._images_dir, "{title}_correlation.png".format(title=title))
        plt.savefig(image_file, bbox_inches="tight")
        # plt.ioff()
    
    def plot_scatter(self, df_numeric, x, y):
        title = "{X} vs {Y}".format(X=x, Y=y)
        plt.figure(figsize=(self._figsize_x, self._figsize_y))
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.scatter(df_numeric[x], df_numeric[y])
        name = "{x}_vs_{y}".replace("\\", " ").replace("/", " ")
        image_file = self._images_dir / "{name}_scatter.png".format(name=name)
        plt.savefig(image_file, bbox_inches="tight")
    
    def plot_histogram(self, df_numeric, x, bins=50, density=True):
        title = "{X} histogram (bins: {bins} kde: {density})".format(X=x, bins=bins, density=density)
        plt.figure(figsize=(self._figsize_x, self._figsize_y))
        plt.title(title)
        plt.ylabel("Frequency")
        plt.xlabel(x)
        if density:
            plt.hist(df_numeric[x], bins=bins, density=density)
            sns.kdeplot(data=df_numeric, x=x)
        else:
            plt.hist(df_numeric[x], bins=bins)
            
        name = x.replace("/", " ").replace("\\", " ")
        image_file = Path.joinpath(self._images_dir, "{name}_histogram.png".format(name=name))
        plt.savefig(image_file, bbox_inches="tight")

    def plot_boxplot(self, df, x, y):
        fig, ax = plt.subplots(figsize=(self._figsize_x, self._figsize_y))
        if y != -1:
            title = "Distribution of {x} vs {y}".format(x=x, y=y)
            sns.boxplot(ax=ax, x=x, y=y, data=df)
            ax.set_title(title)
            ax.set_xlabel(x)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
            name = "{x}_vs_{y}".format(x=x, y=y).replace("/", " ").replace("\\", " ")
        else:
            title = "Distribution of {x}".format(x=x)
            sns.boxplot(ax=ax, x=x, data=df)
            ax.set_title(title)
            name = "{x}".format(x=x).replace("/", " ").replace("\\", " ")
        
        image_file = self._images_dir / "{name}_boxplot.png".format(name=name)
        fig.savefig(image_file, bbox_inches="tight")

        # for name in df_numeric.columns.to_list():
        #     plt.figure(figsize=(self._figsize_x, self._figsize_y))
        #     plt.title(name)
        #     plt.ylabel("Frequency")
        #     plt.xlabel("(bins=50)")
        #     plt.hist(df_numeric[name], bins=50)
        #     name = name.replace("/", " ")
        #     image_file = Path.joinpath(self._images_dir, "{name}.png".format(name=name))
        #     plt.savefig(image_file, bbox_inches="tight")
        #     plt.ioff()
    
    # def plot_counts_vs_word(self, frequencies_by_column):
    #     for column_name in frequencies_by_column.keys():
    #         title = "Word Counts by " + column_name
    #         plt.figure(figsize=(self._figsize_x, self._figsize_y))
    #         # plt.ion()
    #         plt.title(title)
    #         plt.ylabel("Counts")
    #         plt.xticks(rotation=90)
    #         plt.bar(frequencies_by_column[column_name].keys(), frequencies_by_column[column_name].values())
    #         image_file = Path.joinpath(self._images_dir, "{title}.png".format(title=title))
    #         plt.ioff()
    #         plt.savefig(image_file, bbox_inches="tight")
        
    # def plot_wordcloud(self, frequencies_by_column):
    #     for column_name in frequencies_by_column.keys():
    #         word_cloud = WordCloud(background_color="white", width=1200, height=400).generate_from_frequencies(frequencies_by_column[column_name])
    #         image_file = Path.joinpath(self._images_dir, "WordCloud by {name}.png".format(name=column_name))
    #         plt.figure(figsize=(self._figsize_x, self._figsize_y))
    #         plt.imshow(word_cloud, interpolation="bilinear")
    #         plt.axis("off")
    #         plt.ioff()
    #         word_cloud.to_file(image_file)
    
    # def plot_row_length(self, df_with_row_length):
    #     for name in df_with_row_length.columns.to_list():
    #         title = "Row Length in " + name
    #         plt.figure(figsize=(self._figsize_x, self._figsize_y))
    #         plt.title(title)
    #         plt.ylabel("Count")
    #         plt.xlabel("Row Length")
    #         plt.hist(df_with_row_length[name])
    #         image_file = Path.joinpath(self._images_dir, "{title}.png".format(title=title))
    #         plt.savefig(image_file, bbox_inches="tight")
    #         plt.ioff()
        
        
        