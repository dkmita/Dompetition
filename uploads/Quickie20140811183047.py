from competitor import Competitor
import random

class Quickie(Competitor):
    
    moves_dict = {'S':'R', 'R':'P', 'P':'S'} # move : what beats that move

    def __init__(self):
        self.opponents_moves = []
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        self.opponents_moves.append(opponents_move)
        if len(self.opponents_moves) >= 3:
            if (self.opponents_moves[-1] == self.opponents_moves[-2] and
                self.opponents_moves[-2] == self.opponents_moves[-3]):
                return (moves_dict[opponents_move], 'how you like them apples?')
            
        return (random.choice(moves_dict.keys()), 'how you like them apples?')
