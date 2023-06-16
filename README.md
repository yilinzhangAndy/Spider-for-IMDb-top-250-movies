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
      <li><a href="#installation">Installation</a></li>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#authors">Authors</a></li>
  </ol>
</details>




<!-- ABOUT THE PROJECT -->
## About The Project

This package is used to crawl the basic information of the top250 movies on IMDb, and provides data visualization of the global interface and analysis of individual movie data, and able to produce pdf reports.

## Dependencies
  
### Setup (and activate) your environment
```sh
conda env create -f environment.yml
```
  
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
  

  
 *[movie.py](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies/blob/main/spider_tools/Data_Visualization.py)
  ```sh
  from spider_tools.movie import Movie
  ```
  1. Import package:`from spider_tools.movie import Movie`
  2. To initialize the class, the movie's name should be input:`Movie('./data/IMDb.xls', title)`
  3. To check if the movie is in the 250 movies list, it will return a string to tell user the result:`Movie.match_title()`
  4. Print the basic information for the movie:`Movie.print_info()`
  5. Plot generate budget and worldwide gross comparison charts based on movies of the same genre, the result will be saved in movie_chart:`Movie.generate_histogram()`
  6. It will generated a pdf report and saved in movie_pdf:`Movie.output_pdf()`
### Alternative: Import the Conda environment



  ```sh
 conda env create -f environment.yaml
  ```



### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/catiaspsilva/README-template.git
   ```
2. Setup (and activate) your environment
  ```sh
  conda env create -f requirements.yml
  ```

<!-- USAGE EXAMPLES -->
## Usage

1. data: There is a .xls file named IMDb.xls in the folder, which is all the information of 250 movies crawled from IMDb
2. movie_chart: This folder will generate budget and global gross revenue comparison charts based on one type of movie
3. movie_pdf: A report of one movie will be generated in this folder
4. plot_html: The movie ratio, word frequency, and movie year drawn by pyechatrs are all saved in this folder
5. spider_tools: This folder contains all the libraries created by our team:
spider_IMDb.py: This package is used to grab all the basic information of 250 movies and save them. But because the administrator of the IMDb website has added a detection to judge whether it is a human or a robot, it cannot run
<!-- ROADMAP -->
## Roadmap
See the [open issues](https://github.com/catiaspsilva/README-template/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- Authors -->
## Authors


Project Link:  [Spider-for-IMDb-top-250-movies](https://github.com/yilinzhangAndy/Spider-for-IMDb-top-250-movies)



## Thank you
