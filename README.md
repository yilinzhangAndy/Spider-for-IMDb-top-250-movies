# Spider-for-IMDb-top-250-movies

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/catiaspsilva/README-template">
    <img src="image/imdb.png" alt="Logo" width="150" height="150">
  </a>
  



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <li><a href="#dependencies">Dependencies</a></li>
      </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#authors">Authors</a></li>
  </ol>
</details>




<!-- ABOUT THE PROJECT -->
## About The Project

This package is used to crawl the basic information of the top250 movies on IMDb, and provides data visualization of the global interface and analysis of individual movie data, and able to produce pdf reports.

To import this package, the user could add the from `spider_tools.Data_Visualization import Data` and the from `spider_tools.movie import Movie on the begin of code`.

## Dependencies
  
### Setup (and activate) your environment
```sh
conda env create -f environment.yml
```
* [Spider_IMDb.py](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies/blob/main/spider_tools/spider_IMDb.py)

This package is use to crawled all of the basic information of the 250 movies and save. However, because of the administrator of IMDb website add a detection to judge human or robot, it is not longer to run.
  
* [Data_Visualization.py](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies/blob/main/spider_tools/Data_Visualization.py)
```sh
from spider_tools.Data_Visualization import Data
```
  
This package is use to do export the global results of 250 movies, and the functions are:

Import package:

`from spider_tools.Data_Visualization import Data`
 
Initialize class:
 
`Data('./data/IMDb.xls')`

Import data:
  
`Data.Import()`
  
Clean data, the data getting form the first step should be input, and the cleaned data is the output:

`Data.Cleaning(data)`

Get five values which need for visualization after data statistics, the cleaned data is input, and it will return a 5 length list which include numbers for different countries, name for different countries,a list of years, a list of era years, amd a list of Quantity per era:

`Data.Statistics(clean_data)`

The data after `cleaning()` and `Statistics()` is the input, and it will return 7 visualization plots, which include 1.the Distribution of Country origin 2. Year histogram 3. distribution 4.Year of movies 5. the top 100 most frequent words 6.the proportion of various types of movie 7.the distribution of movie lengths:

`Data.Visualization(clean_data, Statistics_data)`
  

  
* [movie.py](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies/blob/main/spider_tools/movie.py)
```sh
from spider_tools.movie import Movie
```
Import package:

`from spider_tools.movie import Movie`

To initialize the class, the movie's name should be input:

`Movie('./data/IMDb.xls', title)`

To check if the movie is in the 250 movies list, it will return a string to tell user the result:

`Movie.match_title()`

Print the basic information for the movie:

`Movie.print_info()`

Plot generate budget and worldwide gross comparison charts based on movies of the same genre, the result will be saved in movie_chart:

`Movie.generate_histogram()`

It will generated a pdf report and saved in movie_pdf:

`Movie.output_pdf()`

<!-- USAGE EXAMPLES -->
## Usage 

1. data: There is a .xls file named IMDb.xls in the folder, which is all the information of 250 movies crawled from IMDb
2. movie_chart: This folder will generate budget and global gross revenue comparison charts based on one type of movie
3. movie_pdf: A report of one movie will be generated in this folder
4. plot_html: The movie ratio, word frequency, and movie year drawn by pyechatrs are all saved in this folder
5. spider_tools: This folder contains all the libraries created by our team:
6. environment.yml: Conda environment file.
7. Introduction.ipynb: Package tutorial and example.
<!-- ROADMAP -->

<!-- Authors -->
## Authors


Project Link:  [Spider-for-IMDb-top-250-movies](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies)



## Thank you
