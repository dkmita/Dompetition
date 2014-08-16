# -*- coding: utf-8 -*-
"""
Created on Thu Aug 07 20:59:40 2014

@author: Justin
"""

from competitor import Competitor

class LastMoveStrat(Competitor):

    def __init__(self):
        pass

    def process_and_decide(self, state):

        if state.get_opponents_last_guess() == "R":
            return "P"
        elif state.get_opponents_last_guess() == "P":
            return "S"
        elif state.get_opponents_last_guess() == "S":
            return "R"
        else:
            raise ValueError, "%s not a valid state" % state.get_opponents_last_guess()