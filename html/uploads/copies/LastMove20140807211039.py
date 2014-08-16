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
            return ("P", "1 ply")
        elif state.get_opponents_last_guess() == "P":
            return ("S", "1 ply")
        elif state.get_opponents_last_guess() == "S":
            return ("R", "1 ply")
        else:
            return ("P", "whatevs")