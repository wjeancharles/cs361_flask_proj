from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from requests import get
from bs4 import BeautifulSoup as Soup
import zmq

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5557")


options = Options()
options.page_load_strategy = "none"
# options.headless = True


# selenium to navigate to actors page
def get_url_by_actor(actor):
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get("https://www.imdb.com/search/name/")
    driver.implicitly_wait(1)
    driver.find_element(By.NAME, "name").send_keys(actor)
    submit = driver.find_element(By.CLASS_NAME, "primary")
    submit.click()
    actor = driver.find_element(By.LINK_TEXT, actor)
    driver.implicitly_wait(3)
    actor.click()
    return driver.current_url


# selenium to navigate to the movie page
def get_url_by_movie(movie):
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get("https://www.imdb.com/search/title/")
    driver.implicitly_wait(1)
    driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/input").send_keys(movie)
    submit = driver.find_element(By.CLASS_NAME, "primary")
    submit.click()
    driver.implicitly_wait(3)
    title = driver.find_element(By.LINK_TEXT, movie)
    driver.implicitly_wait(3)
    title.click()
    return driver.current_url


# scrape the page
def get_movies(url):
    titles = []
    page = get(url)
    request = page.text
    soup_data = Soup(request, "html.parser")
    movies = soup_data.findAll("div", {"class": "knownfor-title-role"})
    for movie in movies:
        titles.append(movie.find("a", {"class": "knownfor-ellipsis"})["title"])
    return titles


def get_actors(url):
    actors = []
    page = get(url)
    request = page.text
    soup_data = Soup(request, "html.parser")
    people = soup_data.findAll("div", {"class": "sc-bfec09a1-5 dGCmsL"})
    for actor in people:
        person = actor.find("a", {"class": "sc-bfec09a1-1 gfeYgX"}).text
        actors.append(person)
    return actors


def scrape_movies(actor):
    url = get_url_by_actor(actor)
    movies = get_movies(url)
    return movies


def scrape_actors(movie):
    url = get_url_by_movie(movie)
    actors = get_actors(url)
    return actors


# Uses ZMQ to communicate with other services
while True:
    search = socket.recv_pyobj()
    if "actor" == search[0]:
        output = scrape_movies(search[1])
    elif "movie" == search[0]:
        output = scrape_actors(search[1])
    else:
        output = scrape_movies(search[0])
    socket.send_pyobj(output)