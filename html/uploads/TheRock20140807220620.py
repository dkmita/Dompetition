# -*- coding: utf-8 -*-
"""
Created on Thu Aug 07 20:59:40 2014

@author: Justin
"""

from competitor import Competitor

class TheRock(Competitor):

    def __init__(self):
        pass

    def process_and_decide(self, state):
        return ("R", "Can you smell what The Rock is cookin'?")