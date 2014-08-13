from competitor import Competitor



class Checker:

    round = 0
    possible_moves = "RPS"

    def get_opponent_last_move(self):
        self.round += 1
        opponent_move = self.possible_moves[self.round % len(self.possible_moves)]
        print opponent_move
        return opponent_move
    


class Dompetitor(Competitor):

    possible_moves = "RPS"

    # base predictor class
    class Predictor(object):
       
        CORRECT_POINTS = 2
        INCORRECT_POINTS = -1
 
        def __init__(self):
            self.results = []
            self.last_guess = None 


        def process(self, opponent_move, dom_last_move):
            if opponent_move is None:
                assert(False)
            if self.last_guess is None:
                self.results = self.results + [0]
            elif opponent_move == self.last_guess:
                self.results = [self.CORRECT_POINTS] + self.results
            else:
                self.results = [self.INCORRECT_POINTS] + self.results

            
        def get_predictor_weight(self,round_weights): 
            total_weight = 0
            for i in range(min(len(round_weights),len(self.results))):
                total_weight += round_weights[i] * self.results[i]

            return total_weight 

        
        def get_prediction(self):
            assert False, "Predictor " + self.__class__.__name__ + " must implement get_prediction()"



    # finds set patterns    
    class RotatingPredictor(Predictor):
       
        def __init__(self, move_order):
            self.move_order = move_order
            self.move_mod = len(move_order)
            self.round = 0
            super(self.__class__, self).__init__()

        def process(self, opponent_move, dom_last_move):
            self.round += 1
            super(self.__class__, self).process(opponent_move, dom_last_move)

        def get_prediction(self):
            self.last_guess = self.move_order[self.round % self.move_mod]
            return self.last_guess 
                        

    # aggregates the desicions of multiple predictors
    class AggregatePredictor:
        
        def __init__(self, weights):
            self.weights = weights
            self.predictors = []

        def add_predictor(self,predictor):
            self.predictors += [predictor]

        def get_aggregate_prediction(self):
            aggregate_points = [0,0,0]
            for predictor in self.predictors:
                prediction = predictor.get_prediction()
                if prediction is None:
                    continue
                #print predictor.move_order,prediction, predictor.get_predictor_weight(self.weights), " ",
                aggregate_points[prediction] += predictor.get_predictor_weight(self.weights)
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



    def __init__(self):
        self.predictors = []
        self.aggregate_predictors = []
        self.dom_last_move = None
        self.agg_predictor = self.AggregatePredictor([1,1,1,1,1])
        for pattern in [[0],[1],[2],[0,1],[0,2],[1,0],[1,2],[2,0],[2,1],[1,2,0]]:
            predictor = self.RotatingPredictor(pattern)
            self.agg_predictor.add_predictor(predictor) 
            self.predictors += [predictor]


    def get_beating_char(self, prediction):
        beating_int = (prediction + 1) % len(self.possible_moves)
        return self.possible_moves[beating_int]

    def process_and_decide(self, rps_state):
        opponent_move_char = rps_state.get_opponents_last_move()
        if opponent_move_char is None:
            return "P", ""

        # update and verify our state
        opponent_move = self.possible_moves.index(opponent_move_char)
        
        # update predictor states
        for predictor in self.predictors:
            predictor.process(opponent_move,self.dom_last_move)

        agg_prediction = self.agg_predictor.get_aggregate_prediction()
        return self.get_beating_char(agg_prediction), "secret"



if __name__ == "__main__":
    moves = "RPS"
    check = Checker()
    comp = Dompetitor()
    for x in range(8):
        comp.process_and_decide(check)


