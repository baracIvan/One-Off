from flask import request
from socketio_instance import socketio
from flask_socketio import emit, join_room
from game.models import game_manager

@socketio.on('join_lobby')
def handle_join_lobby(data):
    room_code = data['room_code']
    nickname = data['nickname']
    sid = request.sid

    print(f"[SocketIO] join_lobby received from {nickname} for room {room_code}")

    room = game_manager.get_room(room_code)
    if not room:
        print(f"[SocketIO] Room {room_code} not found.")
        return

    # ✅ Check if nickname already exists in room
    if not any(p.nickname == nickname for p in room.players):
        player = game_manager.create_player(nickname, sid)
        room.players.append(player)
        # ✅ If room has no host yet, assign this one
        if room.host_sid is None:
            room.host_sid = sid
    else:
        print(f"[SocketIO] {nickname} already in room {room_code}, skipping re-add")

    join_room(room_code)
    broadcast_player_list(room_code)


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    code_to_update = None

    for code, room in list(game_manager.rooms.items()):
        for player in list(room.players):  # copy to avoid modifying while iterating
            if player.sid == sid:
                room.players.remove(player)
                code_to_update = code

                # Handle host leaving
                if room.host_sid == sid:
                    if room.players:
                        room.host_sid = room.players[0].sid
                    else:
                        del game_manager.rooms[code]
                        return
                break

    if code_to_update:
        broadcast_player_list(code_to_update)


def broadcast_player_list(room_code):
    room = game_manager.get_room(room_code)
    if room:
        player_nicknames = [p.nickname for p in room.players]
        print(f"[Broadcast] Room {room_code} players: {player_nicknames}")

        socketio.emit('update_player_list', {
            'players': player_nicknames,
            'host_sid': room.host_sid
        }, room=room_code)


