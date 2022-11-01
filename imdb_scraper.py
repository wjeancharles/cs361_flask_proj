# Created By: Wesley Jean-Charles
# Last Update: 10/30/22
# CS361 Software Engineering 1
# IMDB Web Scraper

# This microservice scrapes the title,actors and rating from all feature films currently
# stored on the IMDB database starting from the following url:
# https://www.imdb.com/search/title/?title_type=feature&sort=user_rating,desc


import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5555")

url = 'https://www.imdb.com/search/title/?title_type=feature&sort=num_votes,desc'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

headers = {"Accept-Language": "en-US,en;q=0.5"}

# Variables to store the list of movies, stars and ratings
movie_name = []
stars = []
rating = []

# Gathers all the data from the web page and stores it in the variable movie_data
movie_data = soup.findAll('div', attrs={'class': 'lister-item mode-advanced'})

for x in movie_data:
    name = x.h3.a.text
    movie_name.append(name)

    actor = x.find('p', class_='').text
    actor = actor.split("Stars:")
    actor = actor[1].split(",")
    actor[0] = actor[0].replace("\n", "")
    actor[1] = actor[1].replace(" \n", "")
    actor[2] = actor[2].replace(" \n", "")
    actor[3] = actor[3].replace(" \n", "")
    actor[3] = actor[3].replace("\n", "")
    stars.append(actor)

    # rate = x.find('div', class_='inline-block ratings-imdb-rating').text.replace("\n", '')
    # rating.append(rate)

x = 0
film_info = {}

# This loop will put all the movies and stars in a dictionary with the movie name as the key.
while x < len(movie_name):
    film_info[movie_name[x]] = stars[x]

    x = x + 1

# Uses ZMQ to communicate with other services
while True:

    time.sleep(5)
    search = socket.recv()
    search = search.decode('ascii')
    movies = []

    print("searching for movies with " + search)

    for key, value in film_info.items():
        if search in value:
            movies.append([key, value])

    print("sending back movies with " + search)
    socket.send_pyobj(movies)


