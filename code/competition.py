import sys
from competitor import Competitor

class NullWriter(object):
    def write(self, arg):
        pass

class Competition(object):

    is_over = False

    def __init__(self, competitor1, competitor2):
        self.competitor1 = competitor1
        self.competitor2 = competitor2

    def compete(self):
        # dont let competitors print ot stdout
        oldstdout = sys.stdout
        sys.stdout = NullWriter()
        while not self.is_over:
            move1, comment1 = self.competitor1.process_and_decide(self.get_competitor1_state())
            move2, comment2 = self.competitor2.process_and_decide(self.get_competitor2_state())
            self.process_moves_first(move1, comment1, move2, comment2)
        # reenable printing to stdout
        sys.stdout = oldstdout
        print self.get_display()
        return self.get_winner()

    def process_moves_first(self, move1, comment1, move2, comment2):
        invalid_reason = self.is_move_valid(move1)
        if invalid_reason:
            raise Exception(invalid_reason)
        invalid_reason = self.is_comment_valid(comment1)
        if invalid_reason:
            raise Exception(invalid_reason)
        invalid_reason = self.is_move_valid(move2)
        if invalid_reason:
            raise Exception(invalid_reason)
        invalid_reason = self.is_comment_valid(comment2)
        if invalid_reason:
            raise Exception(invalid_reason)
        self.process_moves(move1, comment1, move2, comment2)


    def is_move_valid(self,move):
        raise NotImplementedError( "Need to implement is_move_valid(self, move)" )

    def is_comment_valid(self,move):
        raise NotImplementedError( "Need to implement is_comment_valid(self, move)" )

    def process_moves(self, move1, move2):
        raise NotImplementedError( "Need to implement process_moves(self, move1, move2)" )

    def get_display(self):
        raise NotImplementedError( "Need to implement get_display(self)" )

    def get_competitor1_state(self):
        raise NotImplementedError( "Need to implement get_competitor1_state(self)" )

    def get_competitor2_state(self):
        raise NotImplementedError( "Need to implement get_competitor2_state(self)" )

    def get_winner(self):
        raise NotImplementedError( "Need to implement get_winner(self)" )





