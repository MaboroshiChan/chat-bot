from flask import Flask
from flask_socketio import SocketIO, send
import database

app = Flask(__name__)
socket_io = SocketIO(app, cors_allowed_origins="*")

@socket_io.on('message')
def handle_message(message):
    print('received message: '+message)
    if message != 'User Connected':
        send(message, broadcast=True)

if __name__ == '__main__':
    socket_io.run(app, host='localhost', port=5000)
    