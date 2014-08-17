#!/etc/bin/python

# checker for running locally
class Checker: 
    round = 0 
    possible_moves = "RS" 

    def get_opponents_last_guess(self): 
        opponent_move = POSSIBLE_MOVES[self.round % len(POSSIBLE_MOVES)] 
        print opponent_move,
        self.round += 1 
        return opponent_move 


POSSIBLE_MOVES = "RPS"

# utility function to get the char that beats the prediction int
def get_beating_char(prediction): 
    beating_int = (prediction + 1) % len(POSSIBLE_MOVES) 
    return POSSIBLE_MOVES[beating_int] 

# utitlity that translates a prediction list to chars
def translate_move_order(move_order):
    translation = "'"
    for move in move_order:
        translation += POSSIBLE_MOVES[move]
    translation += "'"
    return translation


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


    def get_streak(self):
        i = 0
        while i < len(self.results):
            if self.results[i] <= 0:
                break
            i += 1
        return max(i-2,0)


# finds set patterns 
class RotatingPredictor(Predictor): 
    
    def __init__(self, move_order): 
        self.move_order = move_order 
        self.move_mod = len(move_order) 
        self.round = 0 
        super(RotatingPredictor, self).__init__() 

    def process(self, opponent_move, dom_last_move):
        self.round += 1
        super(RotatingPredictor, self).process(opponent_move, dom_last_move)

    def get_prediction(self): 
        self.last_guess = self.move_order[self.round % self.move_mod] 
        return self.last_guess, "RP:"+str(translate_move_order(self.move_order))


# finds a competitor who copies your last move 
class LastPredictor(Predictor): 

    def __init__(self): 
        self.dom_last_move = None 
        super(LastPredictor, self).__init__() 

    def process(self, opponent_move, dom_last_move): 
        self.dom_last_move = dom_last_move 
        super(LastPredictor, self).process(opponent_move, dom_last_move) 

    def get_prediction(self): 
        if self.dom_last_move is None: 
            self.last_guess = None 
            return 0, "LM:None"
        self.last_guess = (self.dom_last_move + 1) % len(POSSIBLE_MOVES) 
        return self.last_guess, "LM:"+POSSIBLE_MOVES[self.dom_last_move]


# aggregates the desicions of multiple predictors 
class AggregatePredictor(Predictor): 

    def __init__(self): 
        self.predictors = [] 
        super(AggregatePredictor, self).__init__()

    def add_predictor(self,predictor): 
        self.predictors += [predictor] 


# chooses the best predictor in its predictor list
class BestAggregatePredictor(AggregatePredictor):
    
    def get_prediction(self):
        predictor_scores = []
        for predictor in reversed(self.predictors):
            prediction, comment = predictor.get_prediction()
            predictor_scores += [(sum(predictor.results),-len(predictor.move_order), \
                                 prediction, comment)]
        predictor_scores.sort()
        score, move_order_len, agg_prediction, comment = predictor_scores[-1]
        agg_comment = "BA:(" + comment + ")"
        self.last_guess = agg_prediction
        return agg_prediction, agg_comment


# uses the most successful predictor based on its weights
class WeightedAggregatePredictor(AggregatePredictor):

    def __init__(self, weights):
        self.weights = weights 
        super(WeightedAggregatePredictor, self).__init__()

    def get_prediction(self): 
        aggregate_points = [0,0,0] 
        prediction_scores = {0:[],1:[],2:[]}
        for predictor in self.predictors: 
            prediction = predictor.get_prediction() 
            if prediction is None: 
                continue 
            prediction_scores[prediction] += [(predictor.get_predictor_weight(self.weights)+predictor.get_streak(),predictor.move_order)]
            aggregate_points[prediction] += predictor.get_predictor_weight(self.weights)+predictor.get_streak()
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
        #print " %-25d %-25d %-25d" % (aggregate_points[0],aggregate_points[1],aggregate_points[2]) 
        rvalues = sorted(prediction_scores[0])
        pvalues = sorted(prediction_scores[1])
        svalues = sorted(prediction_scores[2])
        index = 0
        while True:
            rstring = str(rvalues[index]) if len(rvalues)>index else "."
            pstring = str(pvalues[index]) if len(pvalues)>index else "."
            sstring = str(svalues[index]) if len(svalues)>index else "."
            if rstring == "." and pstring =="." and sstring ==".":
                break
            #print " %-25s %-25s %-25s" % (rstring, pstring, sstring)
            index += 1 
        return best_moves[-1], "weighted"



class SimpleDomp: 
    possible_moves = "RPS" 

    def generate_patterns( self, size ):
        # come up with all move patterns of length <= size
        patterns = []
        last_length_patterns = [[]]
        for length_index in range(size):
            length_patterns = []
            for patt in last_length_patterns:
                for move in range(len(POSSIBLE_MOVES)):
                    length_patterns += [patt+[move]]
            patterns += length_patterns
            last_length_patterns = length_patterns
        # remove "duplicates" eg [1,1] is a duplicate of [1]
        short_index = 0
        while short_index < len(patterns):
            long_index = len(patterns)-1
            while long_index > short_index:
                short_pattern = patterns[short_index]
                long_pattern = patterns[long_index]
                if len(short_pattern) == len(long_pattern):
                    long_index -= 1
                    continue
                if len(long_pattern) % len(short_pattern) != 0:
                    long_index -= 1
                    continue
                if short_pattern * (len(long_pattern)/len(short_pattern)) == long_pattern:
                    patterns.pop(long_index)
                long_index -= 1
            short_index += 1
        return patterns

    def __init__(self): 
        self.predictors = [] 
        self.aggregate_predictors = [] 
        self.dom_last_move = None 
        self.rp_agg_predictor = BestAggregatePredictor() 
        for pattern in self.generate_patterns(5):
            predictor = RotatingPredictor(pattern) 
            self.rp_agg_predictor.add_predictor(predictor) 
            self.predictors += [predictor] 
        
        #last_predictor = self.LastPredictor() 
        #self.agg_predictor.add_predictor(last_predictor) 
        #self.predictors += [last_predictor] 


    def process_and_decide(self, rps_state): 
        opponent_move_char = rps_state.get_opponents_last_guess() 
        if opponent_move_char is None: 
            return "P", "" 
        # update and verify our state 
        opponent_move = POSSIBLE_MOVES.index(opponent_move_char) 
        # update predictor states 
        for predictor in self.predictors:
            predictor.process(opponent_move, self.dom_last_move)
        agg_prediction, agg_comment = self.rp_agg_predictor.get_prediction() 
        # choose the thing that beats the prediction and return
        print POSSIBLE_MOVES[agg_prediction], agg_comment
        self.dom_last_move = get_beating_char(agg_prediction)
        return self.dom_last_move, agg_comment 



if __name__ == "__main__": 
    moves = "RPS" 
    check = Checker() 
    comp = SimpleDomp() 
    for x in range(12): 
        comp.process_and_decide(check)
