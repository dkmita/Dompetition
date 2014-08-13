class erock():

    def __init__(self):
        # initialize your competitor
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        # figure out what you want to do and then
        # return a (move, comment) tuple
        return ("P", "get in mah belly!")
