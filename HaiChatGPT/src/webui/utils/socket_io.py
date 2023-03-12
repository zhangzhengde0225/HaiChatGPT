
from flask import request
from flask_socketio import SocketIO, send, emit
from ..app import app

socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    print('Client connected:', client_id)
    print('Connected clients:', len(socketio.server_stats()))

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    print('Client disconnected:', client_id)
    print('Connected clients:', len(socketio.server_stats()))
