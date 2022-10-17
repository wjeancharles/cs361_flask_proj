from flask import Flask, render_template,json
import os

app = Flask(__name__)


@app.route('/')
def home():  # put application's code here
    return render_template("/pages/home.jinja2")

@app.route('/countryProfile')
def country_profile():
    return render_template("/pages/country_profile.jinja2")

@app.route('/fighterProfile')
def fighter_profile():
    return render_template("/pages/fighter_profile.jinja2")

@app.route('/olympicGame')
def olympic_game():
    return render_template("/pages/olympic_games.jinja2")


if __name__ == '__main__':
    app.run(debug=True)
