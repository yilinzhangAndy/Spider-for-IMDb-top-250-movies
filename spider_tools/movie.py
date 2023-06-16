import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import math
import sys
import subprocess
from decimal import Decimal
from pathlib import Path

try:
    import borb
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'borb'])

from borb.pdf import PDF, Document, Page, PageLayout, SingleColumnLayout, Image, \
    Paragraph, Alignment, TableUtil, FixedColumnWidthTable

try:
    import xlrd
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xlrd'])

Folder = './'


class Movie:
    def __init__(self, file_path, title=None, currency_exchange_rate=None):
        """
        The initialization class contains 1. the basic information of the movie to be searched;
                                          2. the basic information of the same type of movie;
                                          3. the ranking of some features;
                                          4. the high, medium and low thresholds of budget and gross worldwide;
                                          5. output information, etc.
        :param file_path: the file path of excel
        :param title: the searched movie name
        :param currency_exchange_rate: a dictionary of the currency exchange rates, which contains "R$", "₩", "€", "¥",
                                       "DEM", "MVR", "FRF", "₹", "£" and "A$" exchange rate with US dollar.
        """
        try:
            self.file_path = file_path
            self.df = pd.read_excel(file_path)
        except (AssertionError, FileNotFoundError, ImportError):
            print("ERROR: File not found or failed to read file. Please check the file path you entered!")
            sys.exit()

        # 1. the basic information of the movie to be searched
        self.title = title
        self.basic_info = None
        self.genre = None
        self.language = None
        self.budget = 0
        self.gross_worldwide = 0
        self.film_rating = None
        self.rating_numbers = None
        self.country = None

        # 2. the basic information of the same type of movie
        self.__related_df = None
        self.__related_movie_name = None
        self.__related_budget_list = None
        self.__related_gross_worldwide_list = None

        # 3. the ranking of some features;
        self.genre_rank = 0
        self.language_rank = None
        self.budget_rank = 0
        self.gross_worldwide_rank = 0
        self.related_budget_rank = 0
        self.related_gross_worldwide_rank = 0
        self.film_rating_rank = 0
        self.rating_numbers_rank = 0
        self.country_rank = None

        # 4. the high, medium and low thresholds of budget and gross worldwide;
        self.__high_budget_limit = 0
        self.__medium_budget_limit = 0
        self.__high_gross_worldwide_limit = 0
        self.__medium_gross_worldwide_limit = 0

        self.data = None
        # 5. output information
        self.basic_info_string = None
        self.genre_rank_info_string = None
        self.language_rank_info_string = None
        self.budget_rank_info_string = None
        self.gross_worldwide_rank_info_string = None
        self.film_rating_rank_info_string = None
        self.rating_numbers_rank_info_string = None
        self.country_rank_info_string = None
        self.amount_info_string = None
        self.table_info_string = None

        # 6. others
        self.__whether_match = False
        self.__budget_list = None                       # the budget list of all top 250 movies
        self.__gross_worldwide_list = None              # the gross worldwide list of all top 250 movies
        self.__language_list = None
        self.__country_list = None
        self.__same_language_num_list = None
        self.__same_country_num_list = None
        if currency_exchange_rate is None:
            self.Currency_Exchange_Rate = {'R$': 0.18482475, '₩': 0.0007474863, '€': 1.0424475, '¥': 0.13893056, '$': 1,
                                           'DEM': 0.53307053, 'MVR': 0.065187916, 'FRF': 0.15893336, '₹': 0.012246969,
                                           '£': 1.2083902, 'A$': 0.67059245}
        else:
            self.Currency_Exchange_Rate = currency_exchange_rate

    def __exchange_rate_conversion(self, param_dataframe, param_feature):
        """
        Currency conversion. From the two columns of budget and gross worldwide in excel IMDb, it is found that
        the types of currencies are different, so all of them need to be converted into US dollars for comparison.
        :param param_dataframe: pd.DataFrame
        :param param_feature:
        :return: List of converted amounts
        """
        money_list = []
        try:
            if len(param_dataframe) == 0:
                return False
            for i in range(len(param_dataframe)):
                money = param_dataframe.iloc[i][param_feature]
                money = money.replace(',', '').replace(' ', '').replace('(estimated)', '').replace('\xa0', '')
                money_find = re.findall(r'(.*?)(\d+\.?\d*)', money)
                try:
                    currency_type = money_find[0][0]
                    amount = money_find[0][1]
                    dollar = 0
                    try:
                        dollar = int(amount) * self.Currency_Exchange_Rate[currency_type]
                    except ValueError:
                        dollar = 0
                    finally:
                        money_list.append(dollar)

                except IndexError:
                    money_list.append(0)
            return money_list
        except (KeyError, TypeError):
            print('ERROR: InputError')
            return False

    def set_boundaries(self, param_dataframe):
        """
        Set Budget and Gross WorldWide high, medium and low bounds based on Dataframe
        :param param_dataframe: pd.DataFrame
        :return:
        """
        budget_list = self.__exchange_rate_conversion(param_dataframe, 'Budget')
        gross_worldwide_list = self.__exchange_rate_conversion(param_dataframe, 'Gross worldwide')
        budget_list.sort()
        gross_worldwide_list.sort()
        medium = int(len(budget_list) / 3)
        high = 2 * medium
        self.__high_budget_limit = budget_list[high]
        self.__medium_budget_limit = budget_list[medium-1]
        self.__high_gross_worldwide_limit = gross_worldwide_list[high]
        self.__medium_gross_worldwide_limit = gross_worldwide_list[medium-1]

    def __set_rank(self, param_feature, param_dataframe=None, param_feature_value=None, param_title=None, parma_list=None):
        """
        Rank according to input feature parameters. This function cannot be called externally, you need to use the set_rank() functions.
        :param param_feature: The feature that needs to be ranked
        :param param_dataframe: pd.DataFrame
        :param param_feature_value: The feature value that needs to be ranked
        :param param_title: movie name
        :param parma_list: The converted list of budget or gross world of all movies or related movies
        :return: rank value
        """
        if param_feature == 'Rating Numbers':
            value_list = param_dataframe[param_feature].to_list()
            value_list_ranked = []
            exchange_param_feature_value = 0
            for i in value_list:
                i_find = re.findall(r'(\d+\.?\d*)(.*?)', i)
                num = float(i_find[0][0])
                if i_find[0][1] == 'M':
                    num *= 1000
                if i == param_feature_value:
                    exchange_param_feature_value = num
                value_list_ranked.append(num)
            value_list_ranked.sort()
            rank = value_list_ranked.index(exchange_param_feature_value) + 1
        elif param_feature in ['Budget', 'Gross worldwide']:
            value_list_ranked = sorted(parma_list)
            if param_feature == 'Budget':
                rank = value_list_ranked.index(self.budget)
            else:
                rank = value_list_ranked.index(self.gross_worldwide)
        elif param_feature in ['Language', 'Country']:
            if param_feature == 'Language':
                param1 = self.language
                param2 = self.__language_list
            else:
                param1 = self.country
                param2 = self.__country_list
            rank = [0 for i in range(len(param1))]
            same_feature_value_num = [0 for i in range(len(param1))]
            for i in range(len(param1)):
                for j in range(len(param2)):
                    if param1[i] in param2[j]:
                        same_feature_value_num[i] += 1
                    if self.df.iloc[j]['Title'] == self.title:
                        rank[i] = same_feature_value_num[i]
            return rank, same_feature_value_num
        else:
            same_feature_value = []
            for i in range(len(param_dataframe)):
                if param_dataframe.iloc[i][param_feature] == param_feature_value:
                    same_feature_value.append(param_dataframe.iloc[i]['Title'])
            rank = same_feature_value.index(param_title) + 1
        return rank

    @staticmethod
    def __split_country_or_language(country_or_language):
        country_or_language_split = country_or_language[0]
        split_flag = 0
        for i in country_or_language[1:]:
            if split_flag == 1:
                country_or_language_split += i
                split_flag = 0
            else:
                if not i.isupper():
                    country_or_language_split += i
                else:
                    country_or_language_split += ',' + i
                if i == ' ':
                    split_flag = 1
        country_or_language_split_list = country_or_language_split.split(',')
        return country_or_language_split_list

    def set_rank(self):
        """
        Sets the movie's rank in different features, such as film rating, country, language, etc.
        Since there are multiple languages and countries in a movie, the static function __split_country_or_language() is used to split them and then rank them.
        :return:
        """

        self.film_rating_rank = self.__set_rank(param_dataframe=self.df, param_feature='Film rating', param_feature_value=self.film_rating, param_title=self.title)
        self.rating_numbers_rank = self.__set_rank(param_dataframe=self.df, param_feature='Rating Numbers', param_feature_value=self.rating_numbers)
        self.budget_rank = self.__set_rank(param_feature='Budget', parma_list=self.__budget_list)
        self.gross_worldwide_rank = self.__set_rank(param_feature='Gross worldwide', parma_list=self.__gross_worldwide_list)

        self.related_budget_rank = self.__set_rank(param_feature='Budget', parma_list=self.__related_budget_list)
        self.related_gross_worldwide_rank = self.__set_rank(param_feature='Gross worldwide', parma_list=self.__related_gross_worldwide_list)

        self.__country_list = []
        self.__language_list = []
        for i in range(len(self.df)):
            self.__country_list.append(self.__split_country_or_language(self.df.iloc[i]['Country']))
            self.__language_list.append(self.__split_country_or_language(self.df.iloc[i]['Language']))

        self.language_rank, self.__same_language_num_list = self.__set_rank(param_feature='Language')
        self.country_rank, self.__same_country_num_list = self.__set_rank(param_feature='Country')

    def __set_genre_relative_movie(self, param_genre, param_title):
        """
        According to the genre of the searched movie, some basic information about related movies of the same genre is generated.
        :param param_genre: the genre of the movie to search for
        :param param_title: the movie title of the searched movie
        :return:
        """
        related_list = []
        related_movie_name = []
        rank = 0
        genre_rank = 0
        for i in range(len(self.df)):
            if self.df.iloc[i]['Genre'] == param_genre:
                rank += 1
                related_list.append(self.df.iloc[i])
                related_movie_name.append(self.df.iloc[i]['Title'])

            if self.df.iloc[i]['Title'] == param_title:
                genre_rank = rank
        self.__related_df = pd.DataFrame(related_list)
        self.__related_movie_name = related_movie_name
        self.__related_budget_list = self.__exchange_rate_conversion(self.__related_df, 'Budget')
        self.__related_gross_worldwide_list = self.__exchange_rate_conversion(self.__related_df, 'Gross worldwide')
        self.genre_rank = genre_rank

    def match_title(self, title=None):
        """
        Search movie based on the movie name entered.
        :param title: the movie name
        :return:
        """
        if title is None:
            title = self.title
        else:
            self.__init__(self.file_path, title)

        self.__whether_match = False
        for i in range(len(self.df)):
            if self.df.iloc[i]['Title'] == title:
                self.__whether_match = True
                self.basic_info = self.df.iloc[i]
                self.genre = self.df.iloc[i]['Genre']
                self.language = self.__split_country_or_language(self.df.iloc[i]['Language'])
                self.film_rating = self.df.iloc[i]['Film rating']
                self.rating_numbers = self.df.iloc[i]['Rating Numbers']
                self.budget = self.__exchange_rate_conversion(self.df.iloc[[i]], 'Budget')[0]
                self.gross_worldwide = self.__exchange_rate_conversion(self.df.iloc[[i]], 'Gross worldwide')[0]
                self.country = self.__split_country_or_language(self.df.iloc[i]['Country'])
                self.__budget_list = self.__exchange_rate_conversion(self.df, 'Budget')
                self.__gross_worldwide_list = self.__exchange_rate_conversion(self.df, 'Gross worldwide')
                self.__set_genre_relative_movie(self.genre, title)
                self.set_boundaries(self.df)
                self.set_rank()
                self.set_print_info()

        if not self.__whether_match:
            try:
                if self.title is None:
                    string = 'Please enter the name of the movie you are searching for!'
                else:
                    string = 'Sorry, the movie cannot be found. Please check the name of the movie ("%s") you searched for.' % title
                raise CannotFindError('%s' % string)
            except CannotFindError as error:
                print(error)
        else:
            print('"%s" has been searched!' % self.title)

    @staticmethod
    def log2(value):
        try:
            return math.log2(value)
        except ValueError:
            return 0

    def generate_histogram(self, param_dataframe=None):
        """
        Generate budget and worldwide gross comparison charts based on movies of the same genre, and then save it.
        :param param_dataframe:
        :return:
        """
        if param_dataframe is None:
            param_dataframe = self.__related_df
        if self.__related_df is None:
            try:
                raise InputError('Invalid data set!')
            except InputError as error:
                print(error)
                sys.exit()
        budget_list = self.__exchange_rate_conversion(param_dataframe, 'Budget')
        gross_worldwide_list = self.__exchange_rate_conversion(param_dataframe, 'Gross worldwide')
        budget_list_log = []
        gross_worldwide_list_log = []
        if budget_list:
            for i in range(len(budget_list)):
                budget_list_log.append(self.log2(budget_list[i]))
                gross_worldwide_list_log.append(self.log2(gross_worldwide_list[i]))
            if len(budget_list) >= 6:
                fig = plt.figure(dpi=300, figsize=(24, 8))
            else:
                fig = plt.figure(dpi=300)
            if len(budget_list) >= 130:
                fontsize = 8
            else:
                fontsize = 12
                if len(budget_list) <= 6:
                    fontsize = 8
            ax = fig.add_subplot(111)
            index = [i for i in range(len(param_dataframe))]
            index_1 = [i + 0.4 for i in index]
            plt.bar(index, gross_worldwide_list_log, 0.4, label='Gross Worldwide')
            plt.bar(index_1, budget_list_log, 0.4, label='Budget')
            red_label_index = 0
            for i in range(len(self.__related_movie_name)):
                if self.__related_movie_name[i] == self.title:
                    red_label_index = i
            plt.xticks(index_1, self.__related_movie_name, rotation=90, fontsize=fontsize)  # The data on the abscissa is rotated by 45
            ax.get_xticklabels()[red_label_index].set_color("red")
            plt.legend()
            plt.xlabel('Movie')
            plt.ylabel('Dollar (log2)')
            plt.title('Budget and Gross Worldwide comparison chart of movies of the %s genre' % self.genre)
            self.data = [budget_list_log, gross_worldwide_list_log]
            fig.show()

            folder = Folder + 'movie_chart'
            if not os.path.exists(folder):
                os.makedirs(folder)
            fig.savefig(r'%s/%s bar chart.jpg' % (folder, self.title), bbox_inches='tight')

    def set_print_info(self):
        """
        When the movie that needs to be searched is found, edit the information that needs to be printed.
        :return:
        """
        if self.__whether_match:
            self.genre_rank_info_string = '"%s" ranked No.%d / %d in %s genre.\n' % (self.title, self.genre_rank, len(self.__related_df), self.genre)
            amount_info_string = ''
            self.language_rank_info_string = '"%s" ranked ' % self.title
            for i in range(len(self.language)):
                self.language_rank_info_string += 'No.%d / %d in %s language movie(s)' % (self.language_rank[i], self.__same_language_num_list[i], self.language[i])
                if i == len(self.language)-1:
                    self.language_rank_info_string += '.\n'
                else:
                    self.language_rank_info_string += ', '

            self.country_rank_info_string = '"%s" ranked ' % self.title
            for i in range(len(self.country)):
                self.country_rank_info_string += 'No.%d / %d in the %s movie(s)' % (self.country_rank[i], self.__same_country_num_list[i], self.country[i])
                if i == len(self.country) - 1:
                    self.country_rank_info_string += '.\n'
                else:
                    self.country_rank_info_string += ', '

            self.film_rating_rank_info_string = '"%s" ranked No.%d in %s film rating movie.\n' % (self.title, self.film_rating_rank, self.film_rating)
            self.rating_numbers_rank_info_string = 'Based on the number of votes (%s) from IMDb users, "%s" was ranked No.%d out of the top 250 movies.\n' % (self.rating_numbers, self.title, self.rating_numbers_rank)

            if self.budget >= self.__high_budget_limit:
                grade = 'high'
                budget_info = '"%s" is a high-budget ($%.2f) movie ' % (self.title, self.budget)
            else:
                if self.budget >= self.__medium_budget_limit:
                    grade = 'mid'
                    budget_info = '"%s" is a mid-budget ($%.2f) movie ' % (self.title, self.budget)
                else:
                    grade = 'low'
                    budget_info = '"%s" is a low-budget ($%.2f) movie ' % (self.title, self.budget)
            budget_info += '(its budget ranks No.%d in the top 250 movies and No.%d / %d in %s genre),' % (self.budget_rank, self.related_budget_rank, len(self.__related_budget_list), self.genre)

            if self.gross_worldwide >= self.__high_gross_worldwide_limit:
                if grade == 'high':
                    gross_worldwide_info = ' and '
                else:
                    gross_worldwide_info = ' but '
                gross_worldwide_info += 'its worldwide gross ($%.2f) is high ' % self.gross_worldwide
            else:
                if self.gross_worldwide >= self.__medium_gross_worldwide_limit:
                    if grade == 'mid':
                        gross_worldwide_info = ' and '
                    else:
                        gross_worldwide_info = ' but '
                    gross_worldwide_info += 'its worldwide gross ($%.2f) is middling ' % self.gross_worldwide
                else:
                    if grade == 'low':
                        gross_worldwide_info = ' and '
                    else:
                        gross_worldwide_info = ' but '
                    gross_worldwide_info += 'its worldwide gross ($%.2f) is low ' % self.gross_worldwide
            gross_worldwide_info += '(it ranks No.%d in the top 250 movies and No.%d / %d in %s genre).\n' % (self.gross_worldwide_rank, self.related_gross_worldwide_rank, len(self.__related_gross_worldwide_list), self.genre)

            amount_info_string += budget_info + gross_worldwide_info
            self.amount_info_string = amount_info_string
            basic_info_string = 'Basic information about "%s": ' % self.title
            self.basic_info_string = basic_info_string

            table_info_string = ''
            table_info_string += ' ' + '-' * 76 + '\n'
            table_info_string += '| All movies in the "%s" genre:' % self.genre + ' ' * (75 - len('| All movies in the %s genre:' % self.genre)) + '|\n'
            table_info_string += ' ' + '-' * 76 + '\n'

            rank = 0
            for i in range(len(self.__related_df)):
                movie_info = self.__related_df.iloc[i]
                rank += 1
                if movie_info['Title'] == self.title:
                    table_info_string += '| \033[31mNo.%d %s\033[0m' % (rank, movie_info['Title'])
                else:
                    table_info_string += '| No.%d %s' % (rank, movie_info['Title'])
                table_info_string += ' ' * (77 - len('| No.%d %s' % (rank, movie_info['Title']))) + '|\n'
            table_info_string += ' ' + '-' * 76
            self.table_info_string = table_info_string

    def print_info(self):
        """
        Print related information about the searched movie.
        :return:
        """
        if self.__whether_match:
            print(self.genre_rank_info_string, end='')
            print(self.language_rank_info_string, end='')
            print(self.country_rank_info_string, end='')
            print(self.film_rating_rank_info_string, end='')
            print(self.rating_numbers_rank_info_string, end='')
            print(self.amount_info_string, end='')
            print(self.basic_info_string)
            print(self.basic_info)
            print(self.table_info_string)
        else:
            print('Sorry, the movie cannot be found. Please check the name of the movie ("%s") you searched for.' % self.title)

    def output_pdf(self):
        """
        Use the borb library to generate a pdf report of the searched movies based on the output information.
        :return:
        """
        print('PDF is being generated...')
        pdf = Document()

        # Create empty Page
        page: Page = Page()

        # Add Page to Document
        pdf.add_page(page)

        # Create PageLayout
        layout: PageLayout = SingleColumnLayout(page)

        # Write title
        layout.add(Paragraph('Report on the Movie "%s"' % self.title,
                             font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))

        layout.add(Paragraph('%s' % self.genre_rank_info_string, font_size=Decimal(10)))
        layout.add(Paragraph('%s' % self.language_rank_info_string, font_size=Decimal(10)))
        layout.add(Paragraph('%s' % self.country_rank_info_string, font_size=Decimal(10)))
        layout.add(Paragraph('%s' % self.film_rating_rank_info_string, font_size=Decimal(10)))
        layout.add(Paragraph('%s' % self.rating_numbers_rank_info_string, font_size=Decimal(10)))
        layout.add(Paragraph('%s' % self.amount_info_string, font_size=Decimal(10)))

        layout.add(Paragraph('Basic information about "%s": ' % self.title, font_size=Decimal(10)))

        # generate FixedColumnWidthTable
        t: FixedColumnWidthTable = FixedColumnWidthTable(
            number_of_rows=len(self.basic_info), number_of_columns=2, margin_top=Decimal(12)
        )

        for i in range(len(self.basic_info)):
            key = str(self.basic_info.keys()[i])
            value = ''
            if key == 'Language':
                for j in range(len(self.language)):
                    value += self.language[j]
                    if j != len(self.language)-1:
                        value += ', '
            elif key == 'Country':
                for j in range(len(self.country)):
                    value += self.country[j]
                    if j != len(self.country)-1:
                        value += ', '
            else:
                # value = str(self.language)
                value = str(self.basic_info.iloc[i])
            t.add(Paragraph(key, font="Helvetica-Bold", font_size=Decimal(8)))          # add table heading
            t.add(Paragraph(value, font_size=Decimal(8)))

        # set properties on all table cells
        t.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))

        layout.add(t)

        current = 0
        while current < len(self.__related_df)-1:
            past = current
            current += 26
            if current >= len(self.__related_df) - 1:
                current = len(self.__related_df)
            table_dataframe = pd.DataFrame(self.__related_df.iloc[[i for i in range(past, current)]], columns=['Title', 'Score']).to_numpy()
            rank = np.array([i + 1 for i in range(past, current)])
            table = np.insert(table_dataframe, 0, values=rank, axis=1)
            table = np.insert(table, 0, values=["Ranking", "Movie", "Score"], axis=0)
            new_page: Page = Page()
            pdf.add_page(new_page)
            layout: PageLayout = SingleColumnLayout(new_page)
            paragraph_string = 'All movies in the "%s" genre' % self.genre
            if current > 26:
                paragraph_string += ' (Continuation):'
            else:
                paragraph_string += ':'

            layout.add(Paragraph(paragraph_string, horizontal_alignment=Alignment.CENTERED))

            layout.add(
                TableUtil.from_2d_array(
                    table
                )
            )

        new_page: Page = Page()
        pdf.add_page(new_page)
        layout: PageLayout = SingleColumnLayout(new_page)

        chart_path = Folder + 'movie_chart/%s bar chart.jpg' % self.title

        if not os.path.exists(chart_path):
            self.generate_histogram(self.__related_df)

        layout.add(
            Image(
                Path(chart_path),
                width=Decimal(450),
                height=Decimal(250),
                horizontal_alignment=Alignment.CENTERED,
            )
        )
        layout.add(Paragraph('Fig1. Budget and Gross Worldwide comparison chart of movies of the %s genre' % self.genre,
                             font_size=Decimal(8), horizontal_alignment=Alignment.CENTERED))
        folder = Folder + 'movie_pdf'
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open('%s/Report on the Movie (%s).pdf' % (folder, self.title), "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)
        print('PDF generation complete!')

    def main(self, title=None):
        if title is None:
            title = self.title
        else:
            self.title = title
        self.match_title(title)
        if self.__whether_match:
            self.print_info()
            self.generate_histogram()
            self.output_pdf()


class InputError(Exception):
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class CannotFindError(Exception):
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self):
        return self.error_info


if __name__ == '__main__':
    search = 'The Godfather Part II'
    movie = Movie('../data/IMDb.xls', search)
    movie.match_title()
    movie.print_info()
    movie.output_pdf()

