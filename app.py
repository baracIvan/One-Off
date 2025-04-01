from flask import Flask, render_template, request, redirect, url_for
from socketio_instance import socketio
from game.models import game_manager
from socket_handlers import broadcast_player_list  # ✅

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret'
socketio.init_app(app)

@app.route('/')
def index():
    return render_template('lobby.html')


@app.route('/create_room_form')
def create_room_form():
    return render_template('create_room_form.html')


@app.route('/create_room', methods=['POST'])
def create_room():
    nickname = request.form.get('nickname')
    answer_time = int(request.form.get('answer_time', 30))
    discussion_time = int(request.form.get('discussion_time', 60))
    voting_time = int(request.form.get('voting_time', 30))
    max_rounds = int(request.form.get('max_rounds', 5))

    timers = {
        'answer': answer_time,
        'discussion': discussion_time,
        'voting': voting_time
    }

    room = game_manager.create_room(None, timers, max_rounds)

    return redirect(url_for('room_lobby', code=room.code, nickname=nickname))


@app.route('/join_room', methods=['POST'])
def join_room():
    nickname = request.form.get('nickname')
    code = request.form.get('room_code_full', '').upper()
    room = game_manager.get_room(code)

    if not room:
        return "Room not found", 404


    return redirect(url_for('room_lobby', code=code, nickname=nickname))


@app.route('/leave_room', methods=['POST'])
def leave_room():
    code = request.form.get('room_code')
    nickname = request.form.get('nickname')
    room = game_manager.get_room(code)

    if not room:
        return redirect(url_for('index'))

    # Get current host nickname
    current_host_nickname = None
    for p in room.players:
        if p.sid == room.host_sid:
            current_host_nickname = p.nickname
            break

    # Remove player from list
    room.players = [p for p in room.players if p.nickname != nickname]

    # Promote new host or destroy room
    if nickname == current_host_nickname:
        if room.players:
            room.host_sid = room.players[0].sid
        else:
            del game_manager.rooms[code]
            return redirect(url_for('index'))

    # ✅ Notify all clients
    broadcast_player_list(code)

    return redirect(url_for('index'))


@app.route('/room/<code>')
def room_lobby(code):
    room = game_manager.get_room(code)
    if room:
        nickname = request.args.get('nickname', '')
        return render_template('room_lobby.html', room=room, nickname=nickname)
    return "Room not found", 404


if __name__ == '__main__':
    socketio.run(app, debug=True)
