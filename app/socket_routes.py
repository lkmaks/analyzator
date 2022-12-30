from app import socketio
from flask_socketio import emit, send
from flask_socketio import join_room
from flask_login import current_user
from app.models import Room
from app import db
import html
from sqlalchemy.orm.session import Session
from sqlalchemy import select


@socketio.on('board_event')
def board_event(data):
    mes = data['mes']
    room = data['room']
    emit('board_event', mes, room=room)
    emit('lobby/board_event', room + ';' + mes, room='lobby')

    pos = Room.query.get(room).position
    arr = mes.split(';')
    if arr[0] == 'undo' and pos != '':
        i = len(pos) - 1
        cnt = 0
        while cnt < 2 or pos[i] != ';':
            if pos[i] == ';':
                cnt += 1
            i -= 1
        pos = pos[:i + 1]
    elif arr[0] == 'add_stone':
        i = arr[1]
        j = arr[2]
        pos += '{};{};'.format(i, j)
    elif arr[0] == 'undo_until':
        i = arr[1]
        j = arr[2]
        arr_pos = pos.split(';')
        arr_pos.pop()
        while len(arr_pos) > 0 and (arr_pos[-2], arr_pos[-1]) != (i, j):
            arr_pos.pop()
            arr_pos.pop()
        pos = ';'.join(arr_pos) + ';'
    Room.query.get(room).position = pos
    db.session.commit()


@socketio.on('room_event')
def room_entry(data):
    if data['mes'] == 'join':
        join_room(data['room'])
        pos = Room.query.get(data['room']).position
        emit('pos_data', pos)
        emit('room_event', data['room'] + ';' + 'new:' + current_user.username, room=data['room'])
        emit('lobby/room_event', data['room'] + 'new:' + current_user.username, room='lobby')


@socketio.on('chat_event')
def chat_event(mes):
    s = '<b>' + current_user.username + '</b>: ' + html.escape(mes)
    emit('chat_event', s, room=str(current_user.temp.first().room_id))


@socketio.on('disconnect_event')
def disconnect(data):
    emit('room_event', data['room'] + 'leave:' + current_user.username, room=str(current_user.temp.first().room_id))
    emit('lobby/room_event', data['room'] + 'leave:' + current_user.username, room='lobby')
    db.session.delete(current_user.temp.first())
    db.session.commit()


import flask

@socketio.on('lobby/watching_lobby')
def watching_lobby(mes):
    rooms = Room.query.all()
    room_ids = []
    for r in rooms:
        room_ids.append(r.id)
    emit('lobby/rooms_added', ';'.join((str(d) for d in room_ids)))
    for r in rooms:
        pos = r.position
        emit('lobby/pos_data', str(r.id) + ';' + pos)
    join_room('lobby')


