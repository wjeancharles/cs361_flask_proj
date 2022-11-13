#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print("Sending request")
message = {"sex": "Men", "category": "Open Class", "origin": "Japan"}
socket.send_pyobj(message)

new_message = socket.recv_pyobj()

print(new_message)
