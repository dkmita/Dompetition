from competitor import Competitor



class Checker:

    round = 0
    possible_moves = "RPS"

    def get_opponent_last_move(self):
        self.round += 1
        return possible_moves[self.round % len(possible_moves)]
    


class Dompetitor(Competitor):

    possible_moves = "RPS"

    def __init__(self):
        self.predictors = []
        self.aggregate_predictors = []
        self.dom_last_move = None
        

    def process_and_decide(self, rps_state):
        opponent_move_char = rps_state.get_opponent_last_move()
        if opponent_move_char is None:
            return "P", ""

        # update and verify our state
        opponent_move = possible_moves.index(opponent_move_str)
        self.opponent_moves += [opponent_move]
        
        # update predictor states
        for predictor in predictors:
            predictor.process(opponent_move,dom_last_move)

        

    # base predictor class
    class Predictor(object):
       
        CORRECT_POINTS = 2
        INCORRECT_POINTS = -1
 
        def __init__(self, move_order):
            self.results = []
            self.last_guess = None 


        def process(self, opponent_move, dom_last_move):
            if opponent_move is None:
                assert(False)
            if self.last_guess is None:
                self.results = self.results + [0]
            elif opponent_move == self.last_guess:
                self.results = self.results + [self.CORRECT_POINTS]
            else:
                self.results = self.results + [self.INCORRECT_POINTS]

            
        def get_predictor_weight(self,round_weights): 
            assert len(round_weights) == len(results), "not enough results from round_weights"
            
            total_weight = 0
            for i in range(len(round_weights)):
                total_weight = round_weights[i] * results[i]

            return total_weight 

        
        def get_prediction(self):
            assert False, "Predictor " + self.__class__.__name__ + " must implement get_prediction()"



    # finds set patterns    
    class RotatingPredictor(Predictor):
       
        def __init__(self, move_order):
            self.move_order = move_order
            self.move_mod = len(move_order)
            self.round = 0

        def process(self, opponent_move, dom_last_move):
            self.round += 1
            super(RotatingPredictor, self).process(opponent_move, dom_last_move)

        def get_prediction(self):
            return self.move_order(self.round % self.move_mod)
                        

    # aggregates the desicions of multiple predictors
    class AggregatePredictor:
        
        def __init__(self, weights):
            self.weights = weights
            self.predictors = []

        def add_predictor( predictor ):
            self.predictors += [predictor]

        def get_aggregate_prediction( self ):
            aggregate_points = [0,0,0]
            for predictor in predictors:
                for i in range(min(len(self.weights),len(predictor.results))):
                    if predictor.last_guess is None:
                        continue
                    aggregate_points[predictor.last_guess] += predictor.get_predictor_weight(self.weights)
            best_moves = []
            best_points = -999999999
            for move in range(len(aggregate_points)):
                points = aggregate_points[move]
                if points > best_points:
                    best_moves = [move]
                    best_points = points
                elif points == best_points:
                    best_moves += [move]
            
            #arbitrarily return the last one
            return best_moves[-1]


check = Checker()
comp = Dompetitor()
for x in range(100):
    print comp.process_and_decide(check)




