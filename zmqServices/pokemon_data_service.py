import zmq
import requests

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5555")

while True:
    #  Wait for next request from client
    message = socket.recv_pyobj()
    print(f"Pokemon Data Service: Received Pokemon Data request for: {message}")

    #  Get Pokemon
    item = requests.get(f'https://pokeapi.co/api/v2/pokemon/{message}')
    if item.status_code == 404:
        socket.send_pyobj('Pokemon Data Service: Could not find pokemon!')
        pass
    elif item.status_code == 200:
        item = item.json()
        socket.send_pyobj(item)
