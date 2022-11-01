# Created By: Wesley Jean-Charles
# Last Update: 10/31/22
# CS361 Software Engineering 1
# IMDB Web Scraper

import zmq
import time

context = zmq.Context()

#  Socket to talk to server
print("Connecting to actor finder server")
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:5555")

while True:
    print("Sending an actor to the scraper... expecting a movie")
    actor = str(input("Give me an actor to send "))
    socket.send_string(actor)
    time.sleep(3)
    message = socket.recv_pyobj()
    print("Movies with along the cast featuring the actor are ", message)
    print()
    time.sleep(3)
