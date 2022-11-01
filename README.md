# CS361 Software Engineering 1

---

## Microservice Communication Contract


### Microservice: IMDB Movie/Actor Search

---
This microservice will be using the ZeroMQ library to request and receive data.

The program receiving the information will need to be setup with the basic ZMQ library and set up a socket to.
Talk to the server.

The following is an example of the basic setup to receive requests.

<!-- Code Blocks -->
```Python
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
```

---
## How to send a Request

---
To send a request, a string containing an actors full name must be sent. Here is an example of a request:

<!-- Code Blocks -->
```Python
    actor = "Brad Pitt"
    socket.send_string(actor)
```
---
## What is being received? 

---
After the request is sent, the imdb scraper will return a list containing a movie and the top four stars of the film.

<!-- Code Blocks -->
```Python
    # Message being sent
    socket.send_pyobj(movies)
    # Sends movies containing Brad Pitt
    
    # Message being received
    message = socket.recv_pyobj()

    # An example of print(message)
    # [['Fight Club', ['Brad Pitt', 'Edward Norton', 'Meat Loaf', 'Zach Grenier']], 
    # ['Se7en', ['Morgan Freeman', 'Brad Pitt', 'Kevin Spacey', 'Andrew Kevin Walker']], 
    # ['Inglourious Basterds', ['Brad Pitt', 'Diane Kruger', 'Eli Roth', 'Mélanie Laurent']]]
```
   
---
![UML Sequence Diagram](https://user-images.githubusercontent.com/76965703/199153389-9a408aea-39e3-4128-9d86-de0de240d80d.png)
