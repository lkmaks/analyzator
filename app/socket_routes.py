from app import socketio
from flask_socketio import emit, send
from flask_socketio import join_room
from flask_login import current_user
from app.models import Room
from app import db
import html


@socketio.on('board_event')
def board_event(data):
    mes = data['mes']
    room = data['room']

    if Room.query.get(room) is None:
        return

    emit('board_event', mes, room=room)
    emit('lobby/board_event', room + ';' + mes, room='lobby')

    pos = Room.query.get(room).position

    pos_arr = list(map(int, pos.split(';')[:-1]))

    moves_present = set()
    for i in range(0, len(pos_arr), 2):
        moves_present.add((pos_arr[i], pos_arr[i + 1]))

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
        if (int(i), int(j)) not in moves_present:
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
def disconnect(room_id):
    emit('lobby/user_left', room_id + ':' + current_user.username, room='lobby')
    db.session.delete(current_user.temp.first())
    db.session.commit()


@socketio.on('lobby/watching_lobby')
def watching_lobby(mes):
    rooms = Room.query.all()

    data = []
    for r in rooms:
        data.append(str(r.id))
        data.append(str(r.name))
        print(r.name)

    emit('lobby/rooms_added', ';'.join(data))

    for r in rooms:
        pos = r.position
        emit('lobby/pos_data', str(r.id) + ';' + pos)
    join_room('lobby')



@socketio.on('lobby/delete_room')
def delete_room(room_id):
    Room.query.filter_by(id=room_id).delete()
    db.session.commit()
    emit('lobby/room_deleted', str(room_id), room=str(room_id))
    emit('lobby/room_deleted', str(room_id), room='lobby')


@socketio.on('lobby/create_room')
def create_table(mes):
    name, user_ids = mes
    room = Room(position='')
    room.name = name
    room.allowed_users = ';'.join(user_ids)

    db.session.add(room)
    db.session.commit()
    emit('lobby/rooms_added', str(room.id) + ';' + room.name, room='lobby')

