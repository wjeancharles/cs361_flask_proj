from flask import Flask, render_template, json, request
# from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import zmq


app = Flask(__name__)

# Variables microservice will require

sex = {"sex": "", "category": "", "origin": ""}
olympic = {"olympic": ""}
country = {"country": ""}


def socket(x):
    # socket.send_pyobj(x)
    # message = socket.recv_pyobj()
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    print("Sending request")
    # message = {"sex": "Men", "category": "Heavyweight", "origin": "France"}
    socket.send_pyobj(x)

    new_message = socket.recv_pyobj()

    return new_message


@app.route('/')
def home():  # put application's code here
    return render_template("/pages/home.jinja2", methods=["POST", "GET"])


@app.route('/countryProfile', methods=["POST", "GET"])
def country_profile():
    return render_template("/pages/country_profile.jinja2", country=country)


@app.route('/fighterProfile', methods=["POST", "GET"])
def fighter_profile():
    return render_template("/pages/fighter_profile.jinja2", sex=sex)


@app.route('/olympicGame', methods=["POST", "GET"])
def olympic_game():
    return render_template("/pages/olympic_games.jinja2", olympic=olympic)


@app.route('/displayInfo1', methods=["POST", "GET"])
def tables1():
    if request.method == "POST":
        request.form.get("search_bar")
        olympic[request.form["search_bar"]] = request.form["year"]
        search = socket(olympic)
    return render_template("/pages/tables.jinja2", search=search)


@app.route('/displayInfo2', methods=["POST", "GET"])
def tables2():
    if request.method == "POST":
        request.form.get("search_bar")
        country[request.form["search_bar"]] = request.form["country"]
        search = socket(country)
    return render_template("/pages/tables.jinja2", search=search)


@app.route('/displayInfo3', methods=["POST", "GET"])
def tables():
    if request.method == "POST":
        request.form.get("search_bar")
        sex["sex"] = request.form["gender"]
        sex["category"] = request.form["weight"]
        print(request.form["weight"])
        sex["origin"] = request.form["country"]
        search = socket(sex)
    return render_template("/pages/tables.jinja2", search=search)

if __name__ == '__main__':
    app.run(debug=True, PORT=5000)
