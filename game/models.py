import uuid
import random
import string

class Player:
    def __init__(self, nickname, sid):
        self.id = str(uuid.uuid4())
        self.nickname = nickname
        self.sid = sid
        self.is_impostor = False
        self.answer = None
        self.vote = None


class RoundData:
    def __init__(self, normal_question, impostor_question, impostor_id):
        self.normal_question = normal_question
        self.impostor_question = impostor_question
        self.impostor_id = impostor_id
        self.answers = {}
        self.votes = {}


class GameRoom:
    def __init__(self, code, host_sid, timers, max_rounds):
        self.code = code
        self.host_sid = host_sid
        self.timers = timers
        self.max_rounds = max_rounds
        self.players = []
        self.current_round = 0
        self.current_phase = 'lobby'
        self.questions = []
        self.round_data = None


class GameManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, host_sid, timers, max_rounds):
        code = self._generate_unique_code()
        room = GameRoom(code, host_sid, timers, max_rounds)
        self.rooms[code] = room
        return room

    def get_room(self, code):
        return self.rooms.get(code)

    def create_player(self, nickname, sid):
        return Player(nickname=nickname, sid=sid)

    def get_player_by_sid(self, sid):
        for room in self.rooms.values():
            for player in room.players:
                if player.sid == sid:
                    return player
        return None

    def _generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if code not in self.rooms:
                return code

game_manager = GameManager()

