
import os
# Gets html
from requests import get
# Parses HTML files
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

headers = {'Accept-Language': 'en-US, en;q=0.5'}
url = 'https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv'

# URL = the site you want to scrape from.
# Headers = specifies what formate to scrape. 
results = get(url, headers=headers)

# Parses all the html
parsed_html = BeautifulSoup(results.text, 'html.parser')

# Looks for all div with the class lister-item mode-advanced which stores
# the movie details. Div is a container in html. 
movie_div = parsed_html.find_all('div', class_='lister-item mode-advanced')

test_movie = movie_div[0]


def clean_html(container):
    '''
    Takes in a parsed html of imdb movie info. Turns it into a list of strings.
    Cleans up the parsed html by removing spaces, empty strings and \n. 
    Returns a dictionary of necessary information.
    '''
    container_text = container.text.split('\n')
    clean_container = [x for x in container_text if x not in ['', ' ']]

    title = clean_container[1]
    year_of_release = clean_container[2].replace('(', '')
    year_of_release = year_of_release.replace(')', '')
    runtime = clean_container[5].replace('min', '')
    genre = clean_container[7].strip()
    imdb_rating = clean_container[8]
    metascore = clean_container[25].strip()
    description = clean_container[28]

    index = 30
    value = clean_container[index]
    director = ''
    while value != '| ':
        director = director + value
        index +=1
        value = clean_container[index]
  

    index = 33
    value = clean_container[index]
    stars = ''
    while value not in ['Votes:']:
        stars = stars + value
        index +=1
        value = clean_container[index]

    votes = clean_container[38].replace(',', '')

    cleaned_html = [
        title, year_of_release, runtime, genre,
        imdb_rating, metascore, description,
        director, stars, votes
    ]

    return cleaned_html

def get_movie_info(movie_div):
    '''
    Takes the movie data and puts it into a dictionary. 
    Returns that dictionary.
    '''
    #Dictionary to store the movie info
    movie_info = {
        'title':[],
        'year_of_release':[],
        'runtime':[],
        'genre':[],
        'imdb_rating':[],
        'metascore':[],
        'description':[],
        'director':[],
        'stars':[],
        'votes':[]
    }

    for container in movie_div:
        data = clean_html(container)
        for info, key in zip(data, movie_info):
            movie_info[key].append(info)
    
    return movie_info

def main():
    movie_info = get_movie_info(movie_div)

    df = pd.DataFrame(
        movie_info, 
        columns=[
            'title',
            'year_of_release',
            'runtime',
            'genre',
            'imdb_rating',
            'metascore',
            'description',
            'director',
            'stars',
            'votes'
        ]
    )

    file_name = 'imdb_data_2022.csv'
    full_path = os.path.join('~/imdb_test/data', file_name)
    df.to_csv(full_path)

main()