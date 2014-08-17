# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 21:01:26 2014

@author: Justin
"""

RPS_INDEX = {
              "R": 0,
              "P": 1,
              "S": 2,
            }

### Characteristic evaluation functions ###
def identity(move):
    return move
            
def loses_to(move):
    if move == "P":
        return "R"
    elif move == "S":
        return "S"
    elif move == "R":
        return "P"
    else:
        raise ValueError, "Invalid move in loses_to_move: %s" % str(move)

def beats(move):
    if move == "P":
        return "S"
    elif move == "S":
        return "R"
    elif move == "R":
        return "P"
    else:
        raise ValueError, "Invalid move in beats_move: %s" % str(move)
        
def get_candidates_from_distribution(dist):
    # dist has form [p(P), p(R), p(S)]
    exp_value = {
                  "P" : dist[0] - dist[2],
                  "R" : dist[2] - dist[1],
                  "S" : dist[1] - dist[0],       
                }        
    return [k for (k, v) in exp_value.items() if v == max(exp_value.values())]

def last_move(my_moves, opp_moves):
    if opp_moves[-1] == "R":
        return [1.0, 0.0, 0.0]
    elif opp_moves[-1] == "P":
        return [0.0, 1.0, 0.0]
    elif opp_moves[-1] == "S":
        return [0.0, 0.0, 1.0]
    else:
        raise ValueError, "Invalid move in last_move: %s" % str(opp_moves[-1])

def my_last_move(my_moves, opp_moves):
    if len(my_moves) == 0:
        return None
        
    if my_moves[-1] == "R":
        return [1.0, 0.0, 0.0]
    elif my_moves[-1] == "P":
        return [0.0, 1.0, 0.0]
    elif my_moves[-1] == "S":
        return [0.0, 0.0, 1.0]
    else:
        raise ValueError, "Invalid move in my_last_move: %s" % str(opp_moves[-1])

def pct_thrown(my_moves, opp_moves):
    num_r = sum([1 for x in opp_moves if x == "R"])
    num_p = sum([1 for x in opp_moves if x == "P"])
    num_s = sum([1 for x in opp_moves if x == "S"])
    
    return [
             float(num_r)/len(opp_moves),
             float(num_p)/len(opp_moves),
             float(num_s)/len(opp_moves),
           ]


class Characteristic(object):
    
    def __init__(self, func, nameStr):
        self.predictions = [] # list of distributinos
        self.results = []
        self.results_1 = [] # loses_to
        self.results_2 = [] # beats
        self.evaluate = func
        self.accuracy = 0.0
        self.name = nameStr
        
    def update(self, actual):
        if self.predictions == []:
            self.results.append(1/3.)
            self.results_1.append(1/3.)
            self.results_2.append(1/3.)
        else:
            rps_candidates = get_candidates_from_distribution(self.predictions[-1])
            self.results.append(self.predictions[-1][RPS_INDEX[actual]] if actual in rps_candidates else 0.0)
            self.results_1.append(self.predictions[-1][RPS_INDEX[beats(actual)]] if beats(actual) in rps_candidates else 0.0)
            self.results_2.append(self.predictions[-1][RPS_INDEX[loses_to(actual)]] if loses_to(actual) in rps_candidates else 0.0)
        
        
    def get_accuracy(self, opp_moves):
        # If you predict, say, [0.4, 0.4, 0.2],then you'll get 0.4 if he threw R or P
        retval = 0.0
        for f in [identity, loses_to, beats]:
            if f == identity:                
                results = self.results
            elif f == loses_to:
                results = self.results_1
            elif f == beats:
                results = self.results_2
            finv = identity
            if f == loses_to:
                finv = beats
            elif f == beats:
                finv = loses_to
            curval = 0.0
            for (i, move) in enumerate(opp_moves):
                rps_predictions = get_candidates_from_distribution(self.predictions[i])
                if finv(move) in rps_predictions:
                    curval += results[i]
                    # curval += self.predictions[i][RPS_INDEX[rps_predictions[0]]]
            retval = max(retval, curval)
            self.accuracy = retval/len(opp_moves)
        return retval/len(opp_moves)
        
    def predict(self, my_moves, opp_moves): # should return naive [p(R), p(P), p(S)]
        dist = self.evaluate(my_moves, opp_moves)
        self.predictions.append(dist)
        return dist
        
    def get_best_dist(self):
        r_sum = [
                  sum(self.results),
                  sum(self.results_1),
                  sum(self.results_2),
                ]
        retdist = [0.0, 0.0, 0.0]
        for (i, s) in enumerate(r_sum):
            if s == max(r_sum):
                retdist[0] += self.predictions[-1][-i % 3]
                retdist[1] += self.predictions[-1][(1-i) % 3]
                retdist[2] += self.predictions[-1][(2-i) % 3]
        return [x/sum(retdist) for x in retdist]

class Strategy(object):
    
    def __init__(self):
        self.last_move    = Characteristic(last_move, "last_move")
        self.my_last_move = Characteristic(my_last_move, "my_last_move")
        self.pct_thrown   = Characteristic(pct_thrown, "pct_thrown")
        self.parameters = [
                            self.last_move,
                            self.my_last_move,
                            self.pct_thrown,
                          ]
        
    def predict_opp_move(self, my_moves, opp_moves):
        # get naive distributions
        for parameter in self.parameters:
            parameter.predict(my_moves, opp_moves)
        
        # get best prediction
        retdist = [0., 0., 0.]
        for parameter in self.parameters:
            a = parameter.get_accuracy(opp_moves)
            d = parameter.get_best_dist()
            retdist[0] += a**2*d[0]
            retdist[1] += a**2*d[1]
            retdist[2] += a**2*d[2]

        return [x/sum(retdist) for x in retdist]
        
    def update_parameters(self, opp_moves):
        for parameter in self.parameters:
            parameter.update(opp_moves[-1])


class Acolyte:

    def __init__(self):
        self.my_moves       = []
        self.your_moves     = []
        self.opp_prediction = [1/3., 1/3., 1/3.]
        self.comment        = ""
        self.strategy       = Strategy()

    def process_and_decide(self, state):
        opp_guess = state.get_opponents_last_guess()
        # First move
        if opp_guess is None:
            self.my_moves.append("P")
            return ("P", "because whatever")
        
        # Do some preprocessing about how my guess did, and adjust strategy accordingly
        self.your_moves.append(opp_guess)
        self.strategy.update_parameters(self.your_moves)
        
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
        # self.comment = ", ".join(["%s: %.4f" % (x, y) for (x, y) in exp_value.items()])
        # self.comment = ", ".join(["%.4f" % x for x in self.opp_prediction])
        # self.comment = ", ".join([str(x.predictions[-1]) for x in self.strategy.parameters])
        self.comment = ", ".join(["%.4f" % x.accuracy for x in self.strategy.parameters])
        
        return (choice, self.comment)