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
        return "P"
    elif move == "R":
        return "S"
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
        
def common_recent(my_moves, opp_moves):
    n = 10
    trunc_moves = opp_moves[-n:]
    num_r = sum([1 for x in trunc_moves if x == "R"])
    num_p = sum([1 for x in trunc_moves if x == "P"])
    num_s = sum([1 for x in trunc_moves if x == "S"])
    n = float(n)
    return [num_r/n, num_p/n, num_s/n]
        
def pattern_search(my_moves, opp_moves):
    n = 0
    max_num = 0
    for i in range(2,int(len(my_moves)/2) + 1):
        num = 0
        for j in range(i):
            r = sum([1 for k in range(int(len(opp_moves)/i)) if opp_moves[j + k*i] == "R"])
            p = sum([1 for k in range(int(len(opp_moves)/i)) if opp_moves[j + k*i] == "P"])
            s = sum([1 for k in range(int(len(opp_moves)/i)) if opp_moves[j + k*i] == "S"])
            num += max(r,p,s)
        if num > max_num:
            max_num = max(num, max_num)
            n = i
            
    # return the right thing
    j = len(opp_moves) % n
    r = sum([1 for k in range(int(len(opp_moves)/n)) if opp_moves[j + k*n] == "R"])
    p = sum([1 for k in range(int(len(opp_moves)/n)) if opp_moves[j + k*n] == "P"])
    s = sum([1 for k in range(int(len(opp_moves)/n)) if opp_moves[j + k*n] == "S"])

    if r == max(r, p, s):
        return [1.0, 0.0, 0.0]
    elif p == max(r, p, s):
        return [0.0, 1.0, 0.0]
    else:
        return [0.0, 0.0, 1.0]

def pct_thrown(my_moves, opp_moves):
    #num_r = sum([1 for x in opp_moves if x == "R"])
    #num_p = sum([1 for x in opp_moves if x == "P"])
    #num_s = sum([1 for x in opp_moves if x == "S"])
   # 
   # return [
   #          float(num_r)/len(opp_moves),
   #          float(num_p)/len(opp_moves),
   #          float(num_s)/len(opp_moves),
   #        ]
    weight = 0.95
    num_r = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "R"])
    num_p = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "P"])
    num_s = sum([weight**(len(opp_moves)-i) for (i, m) in enumerate(opp_moves) if m == "S"])
    total = num_r + num_p + num_s
    return [
             float(num_r)/total,
             float(num_p)/total,
             float(num_s)/total,
           ]


class Characteristic(object):
    
    def __init__(self, func, nameStr):
        self.predictions = []       # list of naive distributions
        self.current_best_dist = [] # not naive!
        self.results = []           # if naive predicts R, actually predict R
        self.results_1 = []         # if naive predicts R, actually predict S
        self.results_2 = []         # if naive predicts R, actually predict P
        self.evaluate = func
        self.accuracy = 0.0
        self.name = nameStr
        self.best_result = []
        
    def update(self, actual):
        if self.predictions == []:
            self.results.append(1/3.)
            self.results_1.append(1/3.)
            self.results_2.append(1/3.)
        else:
            self.results.append(   self.predictions[-1][RPS_INDEX[ actual]           ])
            self.results_1.append( self.predictions[-1][RPS_INDEX[ beats(actual)]    ])
            self.results_2.append( self.predictions[-1][RPS_INDEX[ loses_to(actual)] ])
        
    def get_accuracy(self, opp_moves):
        if self.predictions == []:
            return 1.0
        # If you predict, say, [0.4, 0.4, 0.2],then you'll get 0.4 if he threw R or P
        retval = 0.0
        weight = 0.95
        for f in [identity, loses_to, beats]:
            curval = 0.0
            for (i, move) in enumerate(opp_moves):
                # if naive distribution predicts R
                # and opp actually throws S,
                # curval should get += results_1[i]
                # e.g. if f = loses_to (S = loses_to(R))
                # then we should get results_1
                maxval = max(self.predictions[i-1])
                if self.predictions[i-1][RPS_INDEX[f(move)]] == maxval:
                    # curval += maxval*(weight**(len(opp_moves)-i))
                    curval += maxval
                # print "curval = %f, %.2f" % (curval, (1-weight**(len(opp_moves)))/(1-weight))
            retval = max(retval, curval)
            # self.accuracy = retval*(1-weight**(len(opp_moves)))/(1-weight)
            self.accuracy = retval
            
            if self.name == "a":
                print "curval = %f" % curval                
        
        if self.name == "a":
            print "retval = %f" % retval
            
        return retval/len(opp_moves)
        
    def predict(self, my_moves, opp_moves): # should return naive [p(R), p(P), p(S)]
        dist = self.evaluate(my_moves, opp_moves)
        self.predictions.append(dist)
        return dist
        
    def get_best_dist(self):
        # returns what we think the opponent is most likely to throw
        # (rotated distribution of naive distribution)
        r_sum = [
                  sum(self.results),    # opponent throws what we think he will throw, e.g. P
                  sum(self.results_1),  # opponent throws the thing that loses to what we think he will throw, e.g. R
                  sum(self.results_2),  # opponent throws the thing that beats what we think he will throw, e.g. S
                ]
        print "results for %s so far: %s" % (self.name, str(r_sum))
        print "with results   = %s" % self.results
        print "with results_1 = %s" % self.results_1
        print "with results_2 = %s" % self.results_2
        retdist = [0.0, 0.0, 0.0]
        self.best_result = []
        for (i, s) in enumerate(r_sum):
            if s == max(r_sum):
                self.best_result.append(i)
                if self.name == "a":
                    print "i = %d" % i
                # if naive predicts R and actually predicting loses_to(R) (=S)
                # has been the most successful strategy,
                # return the rotated version that returns
                # S as having the most likely outcome.
                retdist[0] += self.predictions[-1][i % 3]
                retdist[1] += self.predictions[-1][(1+i) % 3]
                retdist[2] += self.predictions[-1][(2+i) % 3]
                
        self.current_best_dist = [x/sum(retdist) for x in retdist]
        
        if self.name == "a":
            print "naive prediction = %s" % str(self.predictions[-1])
            print "rotat prediction = %s" % str(self.current_best_dist)
        return self.current_best_dist

class Strategy(object):
    
    def __init__(self):
        self.last_move     = Characteristic(last_move, "a")
        self.my_last_move  = Characteristic(my_last_move, "b")
        self.pct_thrown    = Characteristic(pct_thrown, "c")
        self.common_recent = Characteristic(common_recent, "d")
        self.parameters = [
                            self.last_move,
                            self.my_last_move,
                            self.pct_thrown,
                            self.common_recent,
                          ]
        
    def predict_opp_move(self, my_moves, opp_moves):
        # get naive distributions
        for parameter in self.parameters:
            print "Predicting next move for %s" % parameter.name
            parameter.predict(my_moves, opp_moves)
        
        # get best prediction
        retdist = [0., 0., 0.]
        print "Determining best prediction"
        for parameter in self.parameters:
            accuracy_mean = 0.1
            # a and d should correspond to each other
            a = parameter.get_accuracy(opp_moves)
            d = parameter.get_best_dist()
            print "For %s, accuracy  = %s" % (parameter.name, a)
            print "For %s, best_dist = %s" % (parameter.name, str(d))
            retdist[0] += (max(a-accuracy_mean,0))**2 * d[0]
            retdist[1] += (max(a-accuracy_mean,0))**2 * d[1]
            retdist[2] += (max(a-accuracy_mean,0))**2 * d[2]

        print "Total predictions: %s" % str(retdist)
        normalization = sum(retdist)
        return [x/normalization for x in retdist]
        
    def update_parameters(self, opp_moves):
        for parameter in self.parameters:
            parameter.update(opp_moves[-1])

class Acolyte():

    def __init__(self):
        self.my_moves       = []
        self.your_moves     = []
        self.opp_prediction = [1/3., 1/3., 1/3.]
        self.comment        = ""
        self.strategy       = Strategy()

    def process_and_decide(self, state):
        self.comment = ""
        opp_guess = state.get_opponents_last_guess()
        
        # First move
        if opp_guess is None:
            self.my_moves.append("P")
            return ("P", "because whatever")
        
       # Do some preprocessing about how my guess did, and adjust strategy accordingly
        print "Updating strategy"
        self.your_moves.append(opp_guess)
        print "So far, opponent has thrown: %s" % self.your_moves
        print "So far,       I have thrown: %s" % self.my_moves
        self.strategy.update_parameters(self.your_moves)
        
        # Try to predict your move given updated strategy: [ p(R), p(P, p(S))]
        self.opp_prediction = self.strategy.predict_opp_move(self.my_moves, self.your_moves)

        print "predictions so far:"
        for parameter in self.strategy.parameters:
            print "predictions for %s: %s" % (parameter.name, parameter.predictions)
        print "self.opp_prediction = %s" % str(self.opp_prediction)

        # Selecting what to throw based on distribution
        exp_value = {
                      "P" : self.opp_prediction[0] - self.opp_prediction[2],
                      "R" : self.opp_prediction[2] - self.opp_prediction[1],
                      "S" : self.opp_prediction[1] - self.opp_prediction[0],
                      #"R" : self.opp_prediction[0] - self.opp_prediction[2],
                      #"S" : self.opp_prediction[2] - self.opp_prediction[1],
                      #"P" : self.opp_prediction[1] - self.opp_prediction[0],       
                    }        
        
        best_candidates = [k for (k, v) in exp_value.items() if v == max(exp_value.values())]

        choice = best_candidates[5*len(self.your_moves) % len(best_candidates)] #no idea if this helps?
        
        self.my_moves.append(choice)
        self.comment += "{" + ",".join(["%.0f" % (100*w.accuracy) for w in self.strategy.parameters]) + "} "
        self.comment += ", ".join(["%s: %5.2f" % (x, y) for (x, y) in exp_value.items()])
        #for param in self.strategy.parameters:
            #self.comment += "[%s," % param.name
            #self.comment += ",".join(["%.0f" % (100*x) for x in param.current_best_dist])
            #self.comment += ",%.0f," % (100*param.accuracy)
            #self.comment += str(param.best_result).replace("[","]").replace("]","").replace(" ","")
            #self.comment += "]"
        # self.comment = ", ".join(["%.4f" % x for x in self.opp_prediction])
        # self.comment = ", ".join([str(x.predictions[-1]) for x in self.strategy.parameters])
        # self.comment += " and "
        # self.comment += ", ".join(["%6.4f" % x.accuracy for x in self.strategy.parameters])
        
        return (choice, self.comment)