from competition import Competition
import random

class War(Competition):

    def __init__(self, competitor1, competitor2, num_turns, num_rounds):
        self.internal_competitor1 = InternalWarCompetitor(num_turns)
        self.internal_competitor2 = InternalWarCompetitor(num_turns)
        self.num_turns = num_turns
        self.num_rounds = num_rounds
        self.available_weights = []
        self.all_weights = []
        self.current_weight = 0
        self.completed_round_count = 0

        self.competitor1_state = WarCompetitionState(self.num_turns)
        self.competitor2_state = WarCompetitionState(self.num_turns)
        self.reset()
        self.setup_next_turn()
        super(self.__class__, self).__init__(competitor1, competitor2)


    def get_competitor1_state(self):
        return self.competitor1_state


    def get_competitor2_state(self):
        return self.competitor2_state


    def reset(self):
        self.available_weights = [x+1 for x in range(self.num_turns)]
        self.internal_competitor1.reset()
        self.internal_competitor2.reset()


    def setup_next_turn(self):
        weight_count = len(self.available_weights)
        self.current_weight = int(random.choice(self.available_weights))
        self.all_weights += [self.current_weight]
        self.available_weights.remove(self.current_weight)
        self.competitor1_state.current_weight = self.current_weight
        self.competitor2_state.current_weight = self.current_weight


    def process_moves(self, move1, comment1, move2, comment2):
        self.internal_competitor1.process_move(int(move1), int(move2), comment1)
        self.internal_competitor2.process_move(int(move2), int(move1), comment2)

        if int(move1) > int(move2):
            self.internal_competitor1.process_turn(self.current_weight, True)
            self.internal_competitor2.process_turn(self.current_weight, False)
        elif int(move2) > int(move1):
            self.internal_competitor1.process_turn(self.current_weight, False)
            self.internal_competitor2.process_turn(self.current_weight, True)
        else:
            self.internal_competitor1.process_turn(self.current_weight, False)
            self.internal_competitor2.process_turn(self.current_weight, False)

        if len(self.available_weights) == 0:
            self.completed_round_count += 1
            if self.internal_competitor1.round_score > self.internal_competitor2.round_score:
                self.internal_competitor1.process_round(True)
                self.internal_competitor2.process_round(False)
            elif self.internal_competitor2.round_score > self.internal_competitor1.round_score:
                self.internal_competitor1.process_round(False)
                self.internal_competitor2.process_round(True)
            else:
                self.internal_competitor1.process_round(False)
                self.internal_competitor2.process_round(False)

            if self.completed_round_count >= self.num_rounds:
                self.is_over = True
                return
            self.reset()

        self.setup_next_turn()


    def get_config(self):
        import math
        turns_power = int(math.log10(self.num_turns))
        turns_mult = self.num_turns / 10**(turns_power-1)
        rounds_power = int(math.log10(self.num_rounds))
        rounds_mult = self.num_rounds / 10**(rounds_power-1)
        return int(10000 * turns_mult + 1000 * turns_power + 10 * rounds_mult +  rounds_power)


    def get_score1(self):
        return self.internal_competitor1.round_win_count

    
    def get_score2(self):
        return self.internal_competitor2.round_win_count

    
    def get_display(self):
        cr1 = self.internal_competitor1
        cr2 = self.internal_competitor2
        move_index = 0
        display = "<span class=header><span class=score>" + \
                  self.competitor1.__class__.__name__ + ": " + str(cr1.round_win_count) + "  " + \
                  self.competitor2.__class__.__name__ + ": " + str(cr2.round_win_count) + \
                  "</span>\n\n"
        display += "Round %3s:                %50s %5s  wt  %-5s %-50s </span>\n" % \
                    ("#", "comment1", "move1", "move2", "comment2" )
        for round_index in range(self.num_rounds):
            display += "="*120 + "\n"
            for turn_index in range(self.num_turns):
                display += " Turn %3s: %5s to %-5s %50s  %4s %s%03d%s %-4s  %-50s \n" % \
                           (turn_index+1, cr1.turn_cum_scores[move_index], cr2.turn_cum_scores[move_index],
                            cr1.comments[move_index], cr1.moves[move_index], cr1.turn_wins_texts[move_index], 
                            self.all_weights[move_index], cr2.turn_wins_texts[move_index], cr2.moves[move_index],
                            cr2.comments[move_index])
                move_index += 1
            display += "="*120 + "\n"
            display += "  Round %3s: %5s to %-5s \n" % (round_index+1, cr1.round_cum_counts[round_index],
                                                   cr2.round_cum_counts[round_index])
        return display


    def is_move_valid(self, move):
        try:
            if int(move) < 1 or int(move) > self.num_turns:
                return str(move) + " not a valid move. Must be between 1 and " + str(self.num_turns)
        except:
            return str(move) + " not a valid move. Must be an integer"

    
    def is_comment_valid(self, comment):
        return None


class WarCompetitionState(object):

    def __init__(self, num_turns):
        self.opponents_last_move = None
        self.num_turns = num_turns
        self.current_weight = 0

    def get_opponents_last_move(self):
        return self.opponents_last_move

    def get_current_weight(self):
        return self.current_weight

    def get_num_turns(self):
        return self.num_turns


class InternalWarCompetitor(object):
    
    def __init__(self, num_turns):
        self.round_win_count = 0
        self.round_cum_counts = []
        self.round_score = 0
        self.turn_cum_scores = []
        self.turn_wins_texts = []
        self.moves = []
        self.comments = []
        self.available_moves = []
        self.num_turns = num_turns

    def reset(self):
        self.round_score = 0
        self.available_moves = [x+1 for x in range(self.num_turns)]
        
    def process_move(self, move, opponents_move, comment):
        self.moves += [move]
        self.available_moves.remove(move)
        self.comments += [comment if len(comment) <= 50 else comment1[:50]]

    def process_turn(self, weight, is_win):
        if is_win:
            self.round_score += weight
            self.turn_wins_texts += ["*"]
        else:
            self.turn_wins_texts += [" "]
        self.turn_cum_scores += [self.round_score]
        print self.turn_cum_scores

    def process_round(self, is_win):
        if is_win:
            self.round_win_count += 1
        self.round_cum_counts += [self.round_win_count]

