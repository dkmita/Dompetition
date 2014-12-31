import sys
from competitor import Competitor


class NullWriter(object):
    def write(self, arg):
        pass


class ResultWriter(object):

    def __init__(self, filename):
        self.file = open(filename, "w")
        self.file.write("testing dom")


class Competition(object):

    is_over = False
    result_writer = None

    def __init__(self, result_filename, competitor1, competitor2):
        self.competitor1 = competitor1
        self.competitor2 = competitor2
        self.result_filename = result_filename

    def compete(self):
        self.result_writer = ResultWriter(self.result_filename)
        # dont let competitors print ot stdout
        oldstdout = sys.stdout
        sys.stdout = NullWriter()
        while not self.is_over:
            move1, comment1 = self.competitor1.process_and_decide(self.get_competitor1_state())
            move2, comment2 = self.competitor2.process_and_decide(self.get_competitor2_state())
            self.check_moves(move1, comment1, move2, comment2)
            self.process_moves(move1, comment1, move2, comment2)
        # reenable printing to stdout
        sys.stdout = oldstdout

        score1 = self.get_score1()
        score2 = self.get_score2()

        print score1, score2
        print self.get_display()
        return score1, score2


    def check_moves(self, move1, comment1, move2, comment2):
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
    

    def get_config(self):
        raise NotImplementedError( "Need to implement get_config(self)" )


    def get_score1(self):
        raise NotImplementedError( "Need to implement get_score1(self)" )

    
    def get_score2(self):
        raise NotImplementedError( "Need to implement get_score2(self)" )


            
            
                    
