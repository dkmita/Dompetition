from competition import Competition

class Rps(Competition):

    WINNING_PAIRS = {"R":"S","P":"R","S":"P"}
    competitor1_total_wins = 0
    competitor2_total_wins = 0
    competitor1_wins = []
    competitor2_wins = []
    competitor1_wins_list = []
    competitor2_wins_list = []
    competitor1_guesses = []
    competitor2_guesses = []
    competitor1_comments = []
    competitor2_comments = []

    def __init__(self, competitor1, competitor2, num_turns):
        self.num_turns = num_turns

        self.competitor1_state = RpsCompetitorState()
        self.competitor2_state = RpsCompetitorState()
        super(self.__class__, self).__init__(competitor1, competitor2)

    def get_competitor1_state(self):
        return self.competitor1_state

    def get_competitor2_state(self):
        return self.competitor2_state

    def process_moves(self, move1, comment1, move2, comment2):
        self.competitor1_guesses += [move1]
        self.competitor1_state.opponents_last_guess = move2
        self.competitor1_comments += [comment1 if len(comment1) <= 50 else comment1[:50]]
        self.competitor2_guesses += [move2]
        self.competitor2_state.opponents_last_guess = move1
        self.competitor2_comments += [comment2 if len(comment2) <= 50 else comment2[:50]]
        if move1 != move2:
            if move2 == self.WINNING_PAIRS[move1]:
                self.competitor1_total_wins += 1
                self.competitor1_wins_list += ["*"]
                self.competitor2_wins_list += [" "]
            else:
                self.competitor2_total_wins += 1
                self.competitor2_wins_list += ["*"]
                self.competitor1_wins_list += [" "]
        else:
            self.competitor1_wins_list += [" "]
            self.competitor2_wins_list += [" "]
        self.competitor1_wins += [self.competitor1_total_wins]
        self.competitor2_wins += [self.competitor2_total_wins]
        if len(self.competitor1_guesses) >= self.num_turns:
            self.is_over = True

    def get_winner(self):
        if self.competitor1_wins > self.competitor2_wins:
            return 1
        elif self.competitor2_wins > self.competitor1_wins:
            return 2
        return 0

    def get_display(self):
        display = "Round %3s:            %50s %-5s %5s %-50s </span>\n" % \
                    ("#", "comment1", "move1", "move2", "comment2" )
        display += "="*120 + "\n"
        for round in range(len(self.competitor1_guesses)):
            display += "Round %3s: %3s to %-3s %50s    %s%s %s%s    %-50s \n" % \
                       (round+1, self.competitor1_wins[round], self.competitor2_wins[round],
                        self.competitor1_comments[round], self.competitor1_wins_list[round],
                        self.competitor1_guesses[round], self.competitor2_guesses[round],
                        self.competitor2_wins_list[round], self.competitor2_comments[round])
        display = "<span class=header><span class=score>" + \
                  self.competitor1.__class__.__name__ + ": " + str(self.competitor1_total_wins) + "  " + \
                  self.competitor2.__class__.__name__ + ": " + str(self.competitor2_total_wins) + \
                  "</span>\n\n" + display
        return display

    def is_move_valid(self, move):
        if move not in "RPS":
            return str(move) + " not a valid move. Valid moves: 'R','P','S'"

    def is_comment_valid(self, comment):
        return None


class RpsCompetitorState(object):

    opponents_last_guess = None

    def get_opponents_last_guess(self):
        return self.opponents_last_guess





