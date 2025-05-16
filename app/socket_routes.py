from app import socketio
from flask_socketio import emit, send
from flask_socketio import join_room
from flask_login import current_user
from app.models import Room
from app import db
import html

def moves_from_string(pos: str) -> list[int]:
    coord_strs = pos.split(';')[:-1]
    if len(coord_strs) < 2:
        return []
    return list(map(int, coord_strs))
    

@socketio.on('board_event')
def board_event(data):
    mes = data['mes']
    room = data['room']

    if Room.query.get(room) is None:
        return

    pos = Room.query.get(room).position

    pos_arr = moves_from_string(pos)

    moves_present = set()
    for i in range(0, len(pos_arr), 2):
        moves_present.add((pos_arr[i], pos_arr[i + 1]))

    arr = mes.split(';')
    if arr[0] == 'undo' and len(pos_arr) < 2:
        return
    
    if arr[0] == 'undo':
        pos_arr.pop()
        pos_arr.pop()
    elif arr[0] == 'add_stone':
        i = int(arr[1])
        j = int(arr[2])
        if (i, j) not in moves_present:
            pos_arr.append(i);
            pos_arr.append(j);
    elif arr[0] == 'undo_until':
        i = arr[1]
        j = arr[2]
        arr_pos = pos.split(';')
        if len(arr_pos) > 0:
            arr_pos.pop()
            while len(arr_pos) > 0 and (arr_pos[-2], arr_pos[-1]) != (i, j):
                arr_pos.pop()
                arr_pos.pop()

            if len(arr_pos) > 0:
                pos = ';'.join(arr_pos) + ';'
            else:
                pos = ''
            pos_arr = moves_from_string(pos)
    str_moves = update_position(room, pos_arr)
    emit('board_putpos', pos_arr, room=room)
    emit('lobby/board_putpos', room + ';' + str_moves, room='lobby')


def update_position(room_id, moves) -> str | None:
    str_moves = ';'.join(str(m) for m in moves) + ';'

    paired = []
    for i in range(0, len(moves), 2):
        paired.append((moves[i], moves[i + 1]))

    if len(paired) != len(set(paired)):
        return

    for move in paired:
        if move[0] not in range(15) or move[1] not in range(15):
            return

    Room.query.get(room_id).position = str_moves
    db.session.commit()
    return str_moves

@socketio.on('board_putpos')
def putpos(data):
    room_id, moves = data
    str_moves = update_position(room_id, moves)

    if str_moves is None:
        return
    
    emit('board_putpos', moves, room=room_id)
    emit('lobby/board_putpos', room_id + ';' + str_moves, room='lobby')
    emit('chat_event', 'Position set', room=room_id)


@socketio.on('set_start_pos')
def set_start_pos(data):
    room_id, moves = data
    str_moves = ';'.join(str(m) for m in moves) + ';'

    paired = []
    for i in range(0, len(moves), 2):
        paired.append((moves[i], moves[i + 1]))

    if len(paired) != len(set(paired)):
        return

    for move in paired:
        if move[0] not in range(15) or move[1] not in range(15):
            return

    Room.query.get(room_id).start_position = str_moves
    emit('chat_event', 'Start position value set', room=room_id)
    db.session.commit()

@socketio.on('make_start_pos')
def make_start_pos(room_id):
    str_moves = Room.query.get(room_id).start_position
    moves = list(map(int, str_moves.replace(';', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ').split()))
    # paired = []
    # for i in range(0, len(moves), 2):
    #     paired.append((moves[i], moves[i + 1]))

    Room.query.get(room_id).position = str_moves
    db.session.commit()
    emit('board_putpos', moves, room=room_id)
    emit('lobby/board_putpos', room_id + ';' + str_moves, room='lobby')
    emit('chat_event', 'Position set (from start position value)', room=room_id)


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
    room = Room(position='', start_position='')
    room.name = name
    room.allowed_users = ';'.join(user_ids)

    db.session.add(room)
    db.session.commit()
    emit('lobby/rooms_added', str(room.id) + ';' + room.name, room='lobby')

@socketio.on('room/drawline')
def drawline(mes):
    room_id, pos1, pos2 = mes
    if pos1[0] in range(15) and pos1[1] in range(15) \
        and pos2[0] in range(15) and pos2[1] in range(15):
        emit('room/drawline', [pos1, pos2], room=room_id)

#
# @socketio.on('room/setpos')
# def setinit(mes):
#     room_id, pos = mes
#     Room.query.get(room_id).position = pos
#     emit('lobby/room_setpos', pos, room=str(room_id))
#     emit('lobby/room_setpos', pos, room='lobby')