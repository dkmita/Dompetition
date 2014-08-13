# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 21:01:26 2014

@author: Justin
"""

from competitor import Competitor

class Strategy(object):
    
    def __init__(self):
        # parameters
        pass
        
    def predict_opp_move(self, my_moves, opp_moves):
        weight = 0.5
        num_r = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "R"])
        num_p = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "P"])
        num_s = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "S"])
        total = num_r + num_p + num_s
        return [
                 float(num_r)/total,
                 float(num_p)/total,
                 float(num_s)/total,
               ]
        
    def update_parameters(self, prediction, actual):
        pass


class DumbStrat90(Competitor):

    def __init__(self):
        self.my_moves = []
        self.your_moves = []
        self.opp_prediction = ""
        self.strategy = Strategy()
        self.comment = ""

    def process_and_decide(self, state):
        # First move
        if state.get_opponents_last_guess() is None:
            self.my_moves.append("P")
            return ("P", "because whatever")
            
        # Do some preprocessing about how my guess did, and adjust strategy accordingly
        self.your_moves.append(state.get_opponents_last_guess())
        self.strategy.update_parameters(self.opp_prediction, state.get_opponents_last_guess())
        
        # Try to predict your move given updated strategy: [ p(R), p(P, p(S))]
        self.opp_prediction = self.strategy.predict_opp_move(self.my_moves, self.your_moves)

        # Selecting what to throw based on distribution
        exp_value = {
                      "P" : self.opp_prediction[0] - self.opp_prediction[2],
                      "R" : self.opp_prediction[2] - self.opp_prediction[1],
                      "S" : self.opp_prediction[1] - self.opp_prediction[0],       
                    }        
        
        best_candidates = [k for (k, v) in exp_value.items() if v == max(exp_value.values())]

        choice = best_candidates[5*len(self.your_moves) % len(best_candidates)] #no idea if this helps?
        
        self.my_moves.append(choice)
        self.comment = ", ".join(["%s: %.3f" % (t, p) for (t, p) in exp_value.items()])
        
        return (choice, self.comment)