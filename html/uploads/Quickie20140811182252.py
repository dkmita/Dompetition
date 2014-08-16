class Quickie():

    import random

    moves_dict = {'S':'R', 'R':'P', 'P':'S'} # move : what beats that move

    def __init__(self):
        self.opponents_moves = []
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        self.opponents_moves.append(opponents_move)
        if len(opponents_moves) >= 3:
            if (opponents_moves[-1] == opponents_moves[-2] and
                opponents_moves[-2] == opponents_moves[-3]):
                return (moves_dict[opponents_moves], 'how you like them apples?')
            
        return (random.choice(moves_dict.keys()), 'how you like them apples?')
