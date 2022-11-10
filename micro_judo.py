import pandas as pd
from pandas.core.indexes.numeric import Int64Index
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
import json
import time
import zmq

# collect the data
scraper = pd.read_html("https://en.wikipedia.org/wiki/List_of_Olympic_medalists_in_judo")

# data cleaning
scraper[2].loc[2, "Games"] = "1968 Mexico City details"

# hard coded list of table data
tables = [["Men", "Extra Lightweight"],
          ["Men", "Half Lightweight"],
          ["Men", "Lightweight"],
          ["Men", "Half Middleweight"],
          ["Men", "Middleweight"],
          ["Men", "Half Heavyweight"],
          ["Men", "Heavyweight"],
          ["Men", "Open Class"],
          ["Women", "Extra Lightweight"],
          ["Women", "Half Lightweight"],
          ["Women", "Lightweight"],
          ["Women", "Half Middleweight"],
          ["Women", "Middleweight"],
          ["Women", "Half Heavyweight"],
          ["Women", "Heavyweight"]]

# hard coded list of medals
medals = ["Gold", "Silver", "Bronze"]

# set up the pipeline
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def country_search(req):
    country = []
    for table in range(len(scraper) - 3):
        for medal in medals:
            for cell in range(len(scraper[table])):
                person = scraper[table][medal][cell]
                if person == "not included in the Olympic program":
                    continue
                elif person == "none awarded":
                    continue
                else:
                    pers = person.split(" \xa0")
                    if pers[1].lower() == req["country"].lower():
                        game = scraper[table]["Games"][cell].split(" ", 1)
                        year = game[0]
                        city = game[1].replace(" details", "")
                        country.append(
                            {"name": pers[0], "sex": tables[table][0], "class": tables[table][1], "medal": medal,
                             "year": year,
                             "city": city})
    country_output = []
    for dictionary in country:
        if dictionary not in country_output:
            country_output.append(dictionary)
    return country_output


def olympic_search(req):
    olympic = []
    for table in range(len(scraper) - 3):
        for row in range(len(scraper[table])):
            game = scraper[table]["Games"][row].split(" ", 1)
            year = game[0]
            city = game[1].replace(" details", "")
            if year == req["olympic"]:
                if not olympic:
                    olympic.append({"city": city})
                category = {"category": tables[table][1], "sex": tables[table][0]}
                olympic.append(category)
                for medal in medals:
                    cell = scraper[table][medal][row].split(" \xa0")
                    olympic[len(olympic) - 1][medal] = [cell[0], cell[1]]
                cell = scraper[table]["Bronze"][row + 1].split(" \xa0")
                olympic[len(olympic) - 1]["Bronze2"] = [cell[0], cell[1]]
                break
    return olympic


def fighter_search(req):
    class Person:
        def __init__(self, name, sex, origin):
            self.name = name
            self.sex = sex
            self.origin = origin
            self.gold = []
            self.silver = []
            self.bronze = []

        def add_medals(self, gold, silver, bronze):
            self.gold.append(gold)
            self.silver.append(silver)
            self.bronze.append(bronze)

    fighters = [Person("Ian", "Men", "canada")]

    if req["sex"] == "Men":
        start = 0
        end = 8
    elif req["sex"] == "Women":
        start = 8
        end = 15
    else:
        start = 0
        end = 15

    cat_tables = []
    if req["category"] is not None:
        for i in range(len(tables)):
            if tables[i][1] == req["category"]:
                cat_tables.append(i)

    for table in range(start, end):
        if table not in cat_tables and req["category"] is not None:
            continue
        sex = tables[table][0]
        category = tables[table][1]
        for row in range(len(scraper[table])):
            game = scraper[table]["Games"][row].replace(" details", "")
            for medal in medals:
                cell = scraper[table][medal][row].split(" \xa0")
                name = cell[0]
                if name == "not included in the Olympic program":
                    continue
                elif name == "none awarded":
                    continue
                else:
                    origin = cell[1]
                    flag = False
                    for fighter in fighters:
                        if name == fighter.name:
                            flag = True
                            break
                    if flag is False:
                        new_person = Person(name, sex, origin)
                        fighters.append(new_person)
                    for fighter in fighters:
                        if name == fighter.name:
                            if medal == "Gold":
                                fighter.add_medals(game + " - " + category, None, None)
                            elif medal == "Silver":
                                fighter.add_medals(None, game + " - " + category, None)
                            else:
                                fighter.add_medals(None, None, game + " - " + category)
    del fighters[0]

    if req["origin"] is not None:
        new_fighters = [x for x in fighters if x.origin == req["origin"]]
    else:
        new_fighters = fighters

    for fighter in new_fighters:
        new1_gold = list(set(fighter.gold))
        new2_gold = [y for y in new1_gold if y is not None]
        new1_silver = list(set(fighter.silver))
        new2_silver = [y for y in new1_silver if y is not None]
        new1_bronze = list(set(fighter.bronze))
        new2_bronze = [y for y in new1_bronze if y is not None]

        fighter.gold = new2_gold
        fighter.silver = new2_silver
        fighter.bronze = new2_bronze

    final_fighters = []
    for fighter in new_fighters:
        final_fighters.append({"name": fighter.name, "origin": fighter.origin, "sex": fighter.sex, "gold": fighter.gold,
                               "silver": fighter.silver, "bronze": fighter.bronze})

    return final_fighters


# given an input message af the form {"country": "some country"}, return judo information for a country

# given an input message af the form {"olympic": "XXXX"}, return judo information from a specific year

# given an input message af the form {"sex": "Men", "category": "some cat, "origin": "some country},
# return judo information for a specific fighter

while True:
    #  Wait for next request from client
    message = socket.recv_pyobj()
    print(f"Received request: {message}")

    # fetch results
    if "country" in message.keys():
        result = country_search(message)
    elif "olympic" in message.keys():
        result = olympic_search(message)
    elif "sex" in message.keys():
        result = fighter_search(message)
    else:
        result = "sorry, wrong format"

    #  Send reply to client
    print("Sending reply")
    socket.send_pyobj(result)
