class RsRps:

    def __init__(self):
        self.opponents_moves = []

    def process_and_decide(self, state):
        self.opponents_moves += [state.get_opponents_last_guess()]
        if len(self.opponents_moves) % 2 == 0:
            return "S","mod 2"
        else:
            return "R","else"

class NoGood:
    def __init__(self):
        pass

    def doNothing(self):
        pass
