# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 22:25:00 2014

@author: Justin
"""

class TheRock():

    def __init__(self):
        # initialize your competitor
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        # figure out what you want to do and then
        # return a (move, comment) tuple
        return ("R", "Can you smell what The Rock is cookin'?")