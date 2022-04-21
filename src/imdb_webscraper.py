
import os
import time
import tqdm
# Gets html
from requests import get
# Parses HTML files
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np



def make_url():
    '''
    Returns a list of urls for each IMDB page for BeautifulSoup to parse.
    '''

    url_list = ['https://www.imdb.com/search/title/?groups=top_1000']

    index = 51
    while index != 1001:
        template_url = f'https://www.imdb.com/search/title/?groups=top_1000&start={index}&ref_=adv_nxt'
        url_list.append(template_url)
        index += 50

    return url_list



def parse_html(url_list):
    '''
    Returns a list of soup objects for each parsed page.
    '''
    soup_list = []
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    # URL = the site you want to scrape from.
    # Headers = specifies what formate to scrape. 
    for url in tqdm.tqdm(url_list, desc='Parsing URLs'):
        response = get(url, headers=headers)
        # Parses all the html
        parsed_html = BeautifulSoup(response.text, 'html.parser')
        # Looks for all div with the class lister-item mode-advanced which stores
        # the movie details. Div is a container in html. 
        movie_div = parsed_html.find_all('div', class_='lister-item mode-advanced')
        soup_list.append(movie_div)

    return soup_list



def clean_html(container):
    '''
    Takes in a parsed html of imdb movie info. 
    Cleans up the parsed html by removing spaces, empty strings, \n and converts certain 
    strings to floats and ints. 
    Returns a dictionary of necessary information.
    '''
    # Contains title and year of release
    
    title = container.find('h3', class_='lister-item-header').find('a').text

    year = container.find(
        'span', class_='lister-item-year'
        ).text.replace('(', '').replace(')','')

    runtime = int(
        container.find(
            'span', class_='runtime'
            ).text.replace(' min', '')
        ) if container.find('span', class_='runtime') else None

    genre = container.find(
            'span', class_='genre'
            ).text.replace('\n', '').strip()

    certificate = container.find(
        'span', class_='certificate'
        ).text if container.find('span', class_='certificate') else None

    imdb_rating = float (
        container.find(
        class_="inline-block ratings-imdb-rating"
        ).find(
            'strong'
            ).text
        )

    metascore = int(
        container.find(
        'span', class_='metascore'
        ).text
    ) if container.find('span', class_='metascore') else None

    description = container.find_all(
        'p', class_='text-muted'
        )[-1].text.replace('\n', '')

    director_stars = container.find('p', class_='').text.split('|')

    director = director_stars[0].replace('\n', '').replace('Director:', '').strip()
    stars = director_stars[1].replace('\n', '').replace('Stars:', '').strip()

    #Stores the text for votes and US gross value.
    list_of_text_muted = [value.text for value in container.find_all('span', class_='text-muted')]

    # Gets the tags for the votes and the gross
    value_tags = container.find_all(attrs={'name':'nv'})
  
    votes = None
    gross = None

    if 'Votes:' in list_of_text_muted:
        votes = int(value_tags[0].text.replace(',', ''))

    if 'Gross:' in list_of_text_muted:
        # Gross income is in millions of USD.
        gross = float(
            value_tags[1].text.replace('$','').replace('M','')
        )

    cleaned_html = [
        title, year, runtime, genre, certificate, 
        imdb_rating, metascore, description, director, 
        stars, votes, gross
    ]

    return cleaned_html

def get_movie_info(soup_list):
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
        'film_rating':[],
        'imdb_rating':[],
        'metascore':[],
        'description':[],
        'director':[],
        'stars':[],
        'votes':[],
        'us_gross_millions':[]
    }

    for movie_page in tqdm.tqdm(soup_list, desc='Extracting info from movies'):
        for movie in movie_page:
            data = clean_html(movie)
            for info, key in zip(data, movie_info):
                movie_info[key].append(info)
    
    return movie_info


def main():
    url_list = make_url()
    soup_list = parse_html(url_list)
    movie_info = get_movie_info(soup_list)

    df = pd.DataFrame(
        movie_info
    )

    file_name = 'imdb_data_2022.csv'
    full_path = os.path.join('~/imdb_test/data', file_name)
    df.to_csv(full_path)

main()