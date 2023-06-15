import requests
import re
from bs4 import BeautifulSoup
import xlwt

class spider_IMDb():
    def __init__(self, movie_number=5, savepath='.\\IMDb.xls'):
        '''
        Parameter initialization
        self.IMDb_chart_url provide the top 250 movies website, cannot change
        self.baseURL is the main page of imdb, cannot change
        self.savepath is the path to save result as a excel file
        self.movie_number is the number of movies user want to get, 0<number<=250
        '''
        self.IMDb_chart_url = 'https://www.imdb.com/chart/top/'
        self.baseURL = 'https://www.imdb.com/'
        self.savepath = savepath
        self.movie_number = movie_number
        if movie_number>250 or movie_number<=0:
            raise ValueError('movie number must in 0-250')

    def __get_url_list__(self):
        '''
        Internal function, not external callable
        get the movies' title url, return List
        '''
        #ask url
        resp = requests.get(self.IMDb_chart_url)
        #transfer html to UTF-8
        bs1 = BeautifulSoup(resp.text, 'html.parser')
        #find the class named titleColumn
        movie_url = bs1.find_all('td', attrs={'class': 'titleColumn'})
        #create the regular expression to get the title text
        movie_url_re = re.compile(r'<a href="(.*?)" title=', re.S)
        #get the title index
        url_list = movie_url_re.findall(str(movie_url))
        return url_list

    def __get_data__(self, url):
        '''
        Internal function, not external callable
        Get the movie's detail, return List
        url: the movies' url

        '''
        #ask url
        resp = requests.get(url)
        #transfer html to UTF-8
        bs = BeautifulSoup(resp.text, 'html.parser')
        #find the boxoffice section
        boxoffice = bs.find('section', attrs={'data-testid': 'BoxOffice'})
        #find the techspecs section
        techspace = bs.find('section', attrs={'data-testid': 'TechSpecs'})
        #find the details section
        detail = bs.find('section', attrs={'data-testid': 'Details'})

        #find the relasedate part, orign part, and language part
        detail_relasedate = detail.find('li', attrs={'role':'presentation', 'class':'ipc-metadata-list__item ipc-metadata-list-item--link', 'data-testid':'title-details-releasedate'})
        detail_relasedate1 = detail_relasedate.find('a', attrs='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
        detail_origin = detail.find('li', attrs={'role':'presentation', 'class':'ipc-metadata-list__item', 'data-testid':'title-details-origin'})
        detail_origin1 = detail_origin.findAll('a', attrs='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
        detail_language = detail.find('li', attrs={'role':'presentation', 'class':'ipc-metadata-list__item', 'data-testid':'title-details-languages'})
        detail_language1 = detail_language.findAll('a', attrs='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')

        #create the regular expressions to get the require information text
        title_re = re.compile(r'class="sc-b73cd867-0.*">(.*)</h1>', re.S)
        year_mpr_re = re.compile(r'span class="sc-8c396aa2-2 itZqyK">(.*?)</span>', re.S)
        hours_re =re.compile(r'<div class="ipc-metadata-list-item__content-container">(.*)<!-- --> <!-- -->hour.*',re.S)
        minutes_re =re.compile(r'.*>(.*)<!-- --> <!-- -->minute.*</div>',re.S)        
        number_re = re.compile(r'<div class="sc-7ab21ed2-3 dPVcnq">(.*?)</div>', re.S)
        score_re =  re.compile(r'<span class="sc-7ab21ed2-1 jGRxWM">(.*?)</span>', re.S)
        genre_re = re.compile(r'<div class="ipc-chip-list__scroller">.*<span class="ipc-chip__text">(.*?)</span>', re.S)
        keywords_re= re.compile(r'"keywords":"(.*?)",')
        boxoffice_re = re.compile(r'<li class="ipc-inline-list__item" role="presentation"><label aria-disabled="false" class="ipc-metadata-list-item__list-content-item" for="_blank" role="button" tabindex="0">(.*?)</label>',re.S)
        detail_re = re.compile(r'>(.*?)</a>')

        #get the require information
        title = title_re.findall(resp.text)[0]
        year = detail_re.findall(str(detail_relasedate1))[0]
        mpr = year_mpr_re.findall(resp.text)[1] if len(year_mpr_re.findall(resp.text))==2 else ' '
        hours = int(hours_re.findall(str(techspace))[0]) if hours_re.findall(str(techspace)) else 0
        minutes = int(minutes_re.findall(str(techspace))[0]) if minutes_re.findall(str(techspace)) else 0
        time = hours*60+minutes
        score = float(score_re.findall(resp.text)[0])
        number = number_re.findall(resp.text)[0]
        genre = genre_re.findall(resp.text)[0]
        language = detail_re.findall(str(detail_language1))
        keywords = keywords_re.findall(resp.text)[0]
        budget = boxoffice_re.findall(str(boxoffice))[0] if boxoffice else ' '
        gross_worldwide = boxoffice_re.findall(str(boxoffice))[-1] if boxoffice else ' '
        country = detail_re.findall(str(detail_origin1))

        #save data as a list
        datalist = [title, year, mpr, time, score, number, genre, language, keywords, budget, gross_worldwide, country]
        return datalist

    def __saveData__(self, movie_list): 
        '''
        Internal function, not external callable
        save data as a excel file, return None
        movie_list: a list include movie's title url
        '''
        print("...saving")
        #create excel
        book = xlwt.Workbook(encoding='utf-8')
        #create sheet
        sheet = book.add_sheet('IWDb top250', cell_overwrite_ok = True)
        #create column list
        col = ('Title','Year','Film rating','Time','Score','Rating Numbers','Genre','Language', 'Keywords', 'Budget', 'Gross worldwide', 'Country')
        #write column in excel sheet
        for i in range(len(col)):
            sheet.write(0,i,col[i])
        #write data in excel sheet
        for i in range(len(movie_list)):
            print("save movie #%d"%(i+1))
            movie = movie_list[i]
            for j in range(len(col)):
                sheet.write(i+1,j,movie[j])
        #save file
        book.save(self.savepath)

    def create_excel(self):
        '''
        callable function
        all steps to create the excel file which include movies' information 
        '''
        #get the url list
        url_list = self.__get_url_list__()
        #create an empty list to save data
        movie_list = []
        #traverse all movies
        for i in range(0,self.movie_number):
            print('get movie #%d'%(i+1))
            #combine the true url
            url = self.baseURL+url_list[i]
            #get the one movie information
            movie = self.__get_data__(url)
            #save to a list
            movie_list.append(movie)
        #save to a excel file
        self.__saveData__(movie_list)
        print('Excel has been saved')