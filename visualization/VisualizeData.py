import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from nltk import FreqDist, word_tokenize, RegexpTokenizer, stem
from snowballstemmer import TurkishStemmer

import time, json
from string import punctuation
from pathlib import Path


class VisualizeData():
    def __init__(self):
        self._figsize_x = 12
        self._figsize_y = 8
    
    def prepare_pieplot(self, df_categorical, column_name):
        data_pieplot = {column_name:[]}
        category_counts = df_categorical.loc[:, column_name].value_counts().to_dict()
        for category, value in category_counts.items():
            data_pieplot.get(column_name).append({"name": category, "y": value})
        return data_pieplot
    
    def prepare_barplot(self, dataframe, cat_col, num_col=None):
        if not num_col:
            return self.prepare_pieplot(dataframe, cat_col)
        else:
            title = "{categoric} vs {numeric}".format(categoric=cat_col, numeric=num_col)
            data_barplot = {title:[]}
            cat_and_num = dataframe.loc[:, [cat_col,num_col]].groupby(cat_col).mean().to_dict()
            for label, value in cat_and_num.get(num_col).items():
                data_barplot.get(title).append({"name": label, "y": round(value,1)})
            return data_barplot
    
    def prepare_scatterplot(self, dataframe, num_col_1, num_col_2):
        title = "{0} vs {1}".format(num_col_1, num_col_2)
        data_scatterplot = {}
        df_copy = dataframe.loc[:, [num_col_1, num_col_2]]
        num_col_pairs = [[int(num_1),int(num_2)] for num_1, num_2 in df_copy.values]
        data_scatterplot.update({title: num_col_pairs})
        return data_scatterplot

    def prepare_timeplot(self, df, x, y1, y2=None, y3=None):
        df_copy = df.copy().sort_values(by=[x])
        x_values = [x_value.strftime("%d/%m/%Y") for x_value in df_copy.loc[:, x].dt.date]
        data_timeplot = [{"x_axis": x_values},]
        for numeric_col in [y1 , y2, y3]:
            if numeric_col:
                data_timeplot.append({"name": numeric_col, "data": df_copy.loc[:,numeric_col].to_list()})
        return data_timeplot
    
    def prepare_boxplot(self, df_numeric, x):
        data = []
        x_axis = [x]
        name = x
        describe_df = df_numeric.loc[:, x].describe().to_dict()
        min_df = describe_df.get("min")
        q_min_df = describe_df.get("25%")
        median_df = describe_df.get("50%")
        q_max_df = describe_df.get("75%")
        max_df = describe_df.get("max")
        data.append([min_df, q_min_df, median_df, q_max_df, max_df])

        q_low = df_numeric.loc[:, x].quantile(0.01)
        q_high = df_numeric.loc[:, x].quantile(0.99)
        outliers = set(df_numeric[(df_numeric["Age"] > q_high) | (df_numeric["Age"] < q_low)]["Age"])
        data_outliers = [[0,outlier] for outlier in outliers]
        
        data_boxplot = {"x_axis": x_axis, "series": [{"name":name, "data":data},{"name":"Outliers", "data":data_outliers}] }
        return data_boxplot

    def prepare_correlation(self, df_numeric):
        data = []
        corr_matrix = df_numeric.corr()
        for row in range(0, corr_matrix.shape[0]):
            for column in range(0, corr_matrix.shape[1]):
                data.append([row, column, round(corr_matrix.iloc[row, column], 4) ])
                
        data_correlation = {"x_y_axis": df_numeric.columns.to_list(), "series":[{"name": "correlation matrix", "data": data}]}
        return data_correlation

    def prepare_histogram(self, df_numeric, x):
        data_histogram = {"name": x, "data": df_numeric.loc[:, x].to_list()}
        return data_histogram

    def prepare_wordcloud(self, text_dict, x):
        word_frequencies = self.freq_dist(text_dict.get(x))
        word_freq_list = []
        data_wordcloud = {}
        for word, freq in word_frequencies.items():
            word_freq_list.append([word, int(freq)])
        data_wordcloud.update({"name": x, "data": word_freq_list})
        return data_wordcloud

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

    def plot_time(self, df, x, y1, y2):
        fig, ax = plt.subplots(figsize=(self._figsize_x, self._figsize_y))
        if y1 != -1 and y2 !=-1:
            title = "{y1}_{y2} vs {x}".format(y1=y1, y2=y2, x=x)
            ax2 = ax.twinx()
            p1 = ax.plot_date(df.loc[:, x], df.loc[:, y1], linestyle='solid', color="blue", label=y1)
            p2 = ax2.plot_date(df.loc[:, x], df.loc[:, y2], linestyle='solid', color="orange", label=y2)
            ax.set_ylabel(y1)
            ax2.set_ylabel(y2)
            ax.set_title(title)
            ax.legend((p1[0], p2[0]),(p1[0].get_label(), p2[0].get_label()))
            name = "{y1}_{y2}_vs_{x}".format(y1=y1, y2=y2, x=x).replace("/", " ").replace("\\", " ")
            
        elif y1 != -1:
            title = "{y1} vs {x}".format(y1=y1, x=x)
            p1 = ax.plot_date(df.loc[:, x], df.loc[:, y1], linestyle='solid', color="blue", label=y1)
            ax.set_ylabel(y1)
            ax.set_title(title)
            ax.legend(p1[0].get_label())
            name = "{y1}_vs_{x}".format(y1=y1, x=x).replace("/", " ").replace("\\", " ")

        elif y2 != -1:
            title = "{y2} vs {x}".format(y2=y2, x=x)
            ax2 = ax.twinx()
            p2 = ax.plot_date(df.loc[:, x], df.loc[:, y2], linestyle='solid', color="blue", label=y2)
            ax.set_ylabel(y2)
            ax.set_title(title)
            ax.legend(p2[0].get_label())
            name = "{y2}_vs_{x}".format(y2=y2, x=x).replace("/", " ").replace("\\", " ")    
        
        fig.autofmt_xdate()
        
        image_file = self._images_dir / "{name}_timeseries.png".format(name=name)
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
        
        
def save_as_json(data_list, json_files_dir, file_name):
    with open( json_files_dir / "{0}.json".format(file_name), "w+", encoding="utf8") as file:
        json.dump(data_list, file, sort_keys=False, indent=None)    