from requests import get
from bs4 import BeautifulSoup as Soup
import pandas as pd
import zmq
import random

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5556")

Title = []
Year = []
Rating = []
Actors = []


def scraper(url):
    request = url.text
    soup_data = Soup(request, "html.parser")
    movies = soup_data.findAll("div", {"class": "lister-item mode-advanced"})

    for movie in movies:
        Title.append(movie.h3.a.text)
        Year.append(movie.find("span", {"class": "lister-item-year text-muted unbold"}).text[1:5])
        Rating.append(movie.find("div", {"class": "inline-block ratings-imdb-rating"})["data-value"])
        stars = movie.find('p', class_="").text
        stars = stars.split("Stars:")
        stars = stars[1].split(",")
        movie_actors = []
        for star in stars:
            movie_actors.append(star.replace(" \n", "").replace("\n", ""))
        Actors.append(movie_actors)


for segment in ["0", "251", "501", "751"]:
    scraper(get("https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,"
                "desc&count=250&start=" + segment + "&ref_=adv_nxt"))
data = list(zip(Title, Year, Rating, Actors))



df = pd.DataFrame(data, columns=["Title", "Year", "Rating", "Actors"])


def get_movies(actor):
    movies = []
    for movie in data:
        for person in movie[3]:
            if person == actor:
                movies.append([movie[0], movie[1], movie[2]])
                continue
    return movies


def get_actors(movie):
    for title in data:
        if movie == title[0]:
            return title[3]


# Uses ZMQ to communicate with other services
while True:
    search = socket.recv_pyobj()
    if "actor" == search[0]:
        output = get_movies(search[1])
    elif "movie" == search[0]:
        output = get_actors(search[1])
    elif "start" == search[0]:
        title = data[random.randint(0, 50)]
        output = [title[0], title[3]]
    socket.send_pyobj(output)
