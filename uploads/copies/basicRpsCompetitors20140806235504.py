from rps import Rps
from competitor import Competitor


class RsRps(Competitor):

    def __init__(self):
        self.opponents_moves = []

    def process_and_decide(self, state):
        self.opponents_moves += [state.get_opponents_last_guess()]
        if len(self.opponents_moves) % 2 == 0:
            return "S","mod 2"
        else:
            return "R","else"


class SspRps(Competitor):

    def __init__(self):
        self.opponents_moves = []

    def process_and_decide(self, state):
        self.opponents_moves += [state.get_opponents_last_guess()]
        if len(self.opponents_moves) % 3 == 0:
            return "P","mod 3"
        else:
            return "S","else"

class RpsRps(Competitor):

    def __init__(self):
        self.opponents_moves = []

    def process_and_decide(self, state):
        self.opponents_moves += [state.get_opponents_last_guess()]
        moves = ["S","R","P"]
        modvalue = len(self.opponents_moves) % 3
        return moves[modvalue], str(modvalue) + " mod 3"

if __name__ == '__main__':
    rps = Rps(RsRps(), RpRps(), 100)
    rps.compete()
