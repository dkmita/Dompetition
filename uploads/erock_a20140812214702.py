class erock():

    def __init__(self):
        # initialize your competitor
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        # figure out what you want to do and then
        # return a (move, comment) tuple
        if opponents_move=="R":
            return ("S", "SLICE!")
        elif opponents_move=="P":
            return ("R", "rock smasha!")
        elif opponents_move=="S":
            return ("P", "imma cova yo azz")
        else:
            return ("S", "GO!")
        
