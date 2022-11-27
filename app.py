# Created by Wesley Jean-Charles
# CS361 Software Engineering 1
# Last updated: 11/27/2022

# Search judo.com a website that allows the user to search for Olympic judo information.

from flask import Flask, render_template, request
import zmq


app = Flask(__name__)

# Variables microservice will require

sex = {"sex": "", "category": "", "origin": ""}
olympic = {"olympic": ""}
country = {"country": ""}


# Socket connecting the microservices to the website using ZMQ
def socket(x):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to judo world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    print("Sending request")
    socket.send_pyobj(x)
    new_message = socket.recv_pyobj()

    return new_message


# Home Page
@app.route('/')
def home():
    return render_template("/pages/home.jinja2", methods=["POST", "GET"])


# Country Profile Page. Lets the user select a country to search for all their
# Olympic medal winners.
@app.route('/countryProfile', methods=["POST", "GET"])
def country_profile():
    return render_template("/pages/country_profile.jinja2", country=country)


# Fighter Profile Page. Shows the user Olympic medal winners fitting certain criteria.
@app.route('/fighterProfile', methods=["POST", "GET"])
def fighter_profile():
    return render_template("/pages/fighter_profile.jinja2", sex=sex)


# Olympic Game Page. Displays the Olympic venue along with all the winners for that year.
@app.route('/olympicGame', methods=["POST", "GET"])
def olympic_game():
    return render_template("/pages/olympic_games.jinja2", olympic=olympic)


# Displays the information from the Olympic Page on a table.
@app.route('/displayInfo1', methods=["POST", "GET"])
def tables1():
    if request.method == "POST":
        request.form.get("search_bar")
        olympic[request.form["search_bar"]] = request.form["year"]
        search = socket(olympic)
        length = len(search)
        page = "olympic"
    return render_template("/pages/tables.jinja2", search=search, length=length, page=page)


# Displays the information from the Country Page on a table.
@app.route('/displayInfo2', methods=["POST", "GET"])
def tables2():
    if request.method == "POST":
        request.form.get("search_bar")
        country[request.form["search_bar"]] = request.form["country"]
        search = socket(country)
        length = len(search)
        page = "country"
    return render_template("/pages/tables.jinja2", search=search, length=length, page=page)


# Displays the information from the Fighter Profile Page on a table.
@app.route('/displayInfo3', methods=["POST", "GET"])
def tables():
    if request.method == "POST":
        request.form.get("search_bar")
        sex["sex"] = request.form["gender"]
        sex["category"] = request.form["weight"]
        sex["origin"] = request.form["country"]
        search = socket(sex)
        length = len(search)
        page = "fighter"
    return render_template("/pages/tables.jinja2", search=search, length=length, page=page)


if __name__ == '__main__':
    app.run(debug=True, PORT=5000)
