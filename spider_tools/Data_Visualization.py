import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts.charts import Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
sns.set_style('ticks')
import warnings
import re
from collections import Counter
from pyecharts.charts import WordCloud
import collections



class Data:
    '''
    1.Import raw data
    2.Data cleaning (Year, Gross, Country)
    3.Data Statistics
    4.Data Visualization
    '''

    def __init__(self,DataName) -> None:
        self.DataName = DataName

    def Import(self):
        '''
        Import data obtained through Spider (IMDb.xls)
        '''
        warnings.filterwarnings('ignore')  # Ignore warning
        plt.rcParams['axes.unicode_minus'] = False  # Solve the symbol can not be displayed
        data = pd.read_excel(self.DataName)
        return data

    def Cleaning(self,data):
        '''

        :param data: raw_data
        :return: cleaned_data
        '''
        # Cleanup Year
        data.dropna(inplace=True)
        data.reset_index(drop=True,inplace=True)
        data.drop_duplicates(['Title'],inplace=True)
        # Separate parts with commas
        data['Year'] = data['Year'].apply(lambda x:x.split(',')[1])
        # Keep numbers only
        data['Year'] = data['Year'].apply(lambda x: re.sub("\D", "", x))

        # Clean Gross
        data.dropna(inplace=True)
        data.reset_index(drop=True,inplace=True)
        data.drop_duplicates(['Title'],inplace=True)
        # Keep numbers only
        data['Gross worldwide'] = data['Gross worldwide'].apply(lambda x: re.sub("\D", "", x))

        # Clean up country
        # Condition on spaces and capital letters
        # If it is jointly filmed by multiple countries
        # the first country will be used as the representative
        def helper(name):
            index = 0
            flag = 0
            countrys = name.split(' ')
            for contr in countrys:
                for i in range(len(contr)):
                    if contr[i].isupper():
                        flag += 1
                        if flag == 2:
                            return name[:index]
                    index += 1
                index += 1
                flag =0
            return name 

        for i in range(len(data['Country'])):
            data['Country'][i] = helper(data['Country'][i])

        return data

    def Statistics(self,data):
        '''
        :param data: cleaned_data
        :return: CountryNum: Numbers for different countries
                 CountryName: Name for different countries
                 Year_era: a list of years. Every 10 years count to one year. Example: 1990 - 1999 all counts to 1990
                 era: a list of era years
                 era_number: a list of Quantity per era
        '''
        # countries
        Con_count = Counter(data['Country'])
        # Convert to dictionary format
        dicCon_count = {number: value for number, value in Con_count.items()}
        # sorted by the value(number)
        sortdicCon_count = sorted(dicCon_count.items(), key=lambda item: item[1])
        dic1Con_count = {k: v for k, v in sortdicCon_count}
        # get key
        xCon_count = [i for i in dic1Con_count.keys()]
        yCon_count = []
        # get value
        for i in dic1Con_count.keys():
            yCon_count.append(dic1Con_count.get(i))

        # Count countries other than the US and UK into one category
        othernum = 0
        for i in range(len(yCon_count)):
            if yCon_count[i] < 20:
                othernum = othernum + yCon_count[i]
        CountryName = ['United States', 'United Kingdom', 'Other Countries']
        CountryNum = [yCon_count[-1], yCon_count[-2], othernum]

        # Year into Chronology
        Y = data.iloc[0:, 1]
        Y_ = pd.to_numeric(Y, errors='coerce').fillna('0').astype('int32')
        Year_era = 10 * (Y_ // 10)
        recounted = Counter(Year_era)
        # Convert to dictionary format
        dic = {number: value for number, value in recounted.items()}
        sortdic = sorted(dic.items())
        dic1 = {k: v for k, v in sortdic}
        # get key
        era = [i for i in dic1.keys()]
        era_number = []
        # get value
        for i in dic1.keys():
            era_number.append(dic1.get(i))

        return [CountryNum,CountryName,Year_era,era,era_number]

    def Visualization(self,data, Statistics_data):
        '''
        :param data: cleaned_data
        :param Statistics_data: the data after use Statistics()
        :return: visualization of 1. the Distribution of Country origin
                                  2. Year histogram and distribution
                                  3. Year of movies
                                  4. the top 100 most frequent words
                                  5. the proportion of various types of movies
                                  6. the distribution of movie lengths
                                  7. the relationship between film length and score
        '''
        CountryNum = Statistics_data[0]
        CountryName = Statistics_data[1]
        Year_era = Statistics_data[2]
        era = Statistics_data[3]
        era_number = Statistics_data[4]

        # set canvas size
        plt.figure(figsize=(12, 6))
        figure, axes = plt.subplots(1, 1, figsize=(6, 6), dpi=120)
        # Customize the color of each sector of the pie chart
        colors = ["#4E79A7", "#A0CBE8", "#F28E2B"]
        # Plot
        plt.pie(CountryNum,
                labels=CountryName,  # Set grouping category labels
                colors=colors,  # color
                # Let the sector with a larger ratio explode,
                # the larger the ratio, the farther away from the center of the circle
                explode=(0.2, 0, 0),
                # Display labels as percentages with two decimal places
                autopct='%.2f%%',
                # The distance position of the group name label relative to the center of the circle
                labeldistance=1.1,
                # The distance position of the value label relative to the center of the circle
                pctdistance=0.9,
                # The relative radius of the pie chart
                radius=1,
                # Starting angle for drawing
                startangle=90,
                # clock direction
                counterclock=False
                )
        plt.title("Distribution of Country origin")
        plt.show()

        sns.displot(Year_era, bins=30, kde=True)

        # Pie chart
        Y_pie = Pie(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
        Y_pie.add(series_name='Year',
                  data_pair=[list(z) for z in zip(era, era_number)],
                  rosetype='radius',
                  radius='60%',
                  )
        Y_pie.set_global_opts(title_opts=opts.TitleOpts(title="Year of movies",
                                                        pos_left='center',
                                                        pos_top=30))
        Y_pie.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger='item', formatter='{a} <br/>{b}:{c} ({d}%)'))
        Y_pie.load_javascript()
        #Y_pie.render_notebook()
        Y_pie.render('./plot_html/Year_of_movie.html')

        result_list = []
        for i in data['Genre'].values:
            word_list = str(i).split(' / ')
            for j in word_list:
                result_list.append(j)
        result_list
        word_counts = collections.Counter(result_list)
        # Word frequency statistics: Get the top 100 most frequent words
        word_counts_top = word_counts.most_common(100)
        #print(word_counts_top)
        wc = WordCloud()
        wc.add('', word_counts_top)
        wc.load_javascript()
        #wc.render_notebook()
        wc.render('./plot_html/Word_frequency.html')

        # Use pie chart to analyze the proportion of various types of movies
        word_counts_top = word_counts.most_common(10)
        a3 = Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
        a3.add(series_name='Genre',
               data_pair=word_counts_top,
               rosetype='radius',
               radius='60%',
               )
        a3.set_global_opts(title_opts=opts.TitleOpts(title="Proportion of films of various genres",
                                                     pos_left='center',
                                                     pos_top=50))
        a3.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger='item', formatter='{a} <br/>{b}:{c} ({d}%)'))
        a3.load_javascript()
        #a3.render_notebook()
        a3.render('./plot_html/Proportion_of_films.html')

        # Analyze the distribution of movie lengths
        sns.displot(data['Time'], bins=30, kde=True)

