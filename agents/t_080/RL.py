# -*- coding: utf-8 -*-
"""
Created on Mon May 23 15:32:56 2022

@author: pc-user
"""

import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
import sys
sys.path.append('agent/t_080/')
import json

THINKTIME = 0.9


class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        
        self.weight = [10,5,-5,0.5]
        self.round = 0
        with open('agents/t_080/astar_hvalue.json', 'r', encoding = 'utf-8') as hList:
            self.hValue = json.load(hList)
        with open('agents/t_080/weight.json', 'r', encoding = 'utf-8') as wList:
            self.weight = json.load(wList)['weight']

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score - score
    
    # Fundamental action function for select each action in different rounds
    def SelectAction(self,actions,pState):
        # Update round times
        self.round += 1
        # Record start time
        startTime = time.time()
        # Best Q-value should be the max of Q(s,a), hence start with smallest
        bestQValue = -999    
        # Initial action set as random
        initialAction = random.choice(actions)
        # Best action initially set as random
        # When over THINKTIME, random choose the action for best action
        bestAction = random.choice(actions)
        # The first five steps apply random action
        if self.round < 6:
            return initialAction
        # compare Q-value and best action after 5 steps
        else:
            for action in actions:
                # Ensure think time is not over 1s
                if time.time() - startTime >THINKTIME:
                    print("TIME OUT")
                    #break
                else:
                    # Calculate Q-value
                    QValue = self.CalQValue(deepcopy(pState),action,actions)
                    # Change best Q-value to max Q-value
                    # Change best action from random to the current action
                    if QValue > bestQValue:
                        bestQValue = QValue
                        bestAction = action
            print(time.time() - startTime)
        return bestAction
    
    # Function for calculating max of Q-value
    def CalQValue(self,state,action,actions):
        # Store feature data from DefineFeatures function into features
        features = self.DefineFeatures(state,action,actions)
        # initial result set as 0
        result = 0
        for i in range(len(features)):
            result += features[i] * self.weight[i]
        return result
    
    # Define features
    def DefineFeatures(self,state,action,actions):
        # Self counter color
        counterColor = 2 * (self.id + 1)
        # Oppositer counter color
        oppoColor = 2 * ((1-self.id) + 1)
        # Store feature values into a list
        features = []
        
        # For feature 1 score
        nextState = deepcopy(state)
        score = self.DoAction(nextState, action)
        features.append(score/3)
        
        # For feature 2 self counters
        number = "".join(map(str,nextState.board))
        features.append(number.count(str(counterColor))/51)
        
        # For feature 3 oppositer counters
        features.append(number.count(str(oppoColor))/51)
        
        # For variation of heuristic
        features.append(self.VariationH(nextState.board)/21)
        
        return features
    
    # Variation of heuristic
    def VariationH(self,board):
        # self ring color
        color = str(2 * (self.id + 1) - 1)
        # initial max Q value set as -999
        maxQValue = -999
        # looking for horizontial, vertical and diagonal
        # set initial as -999
        maxH = maxV = maxD = -999
        for i in range(1, 10):  
            start = max(0, 5-i)
            end = min(7, 12-i)
            if i == 5:
                start = 1
                end = 6
            for j in range(start,end):
                # For horizontial value
                hCode = str(self.id) + str(board[(i,j)]) + str(board[(i,j+1)]) + str(board[(i,j+2)]) + str(board[(i,j+3)]) + str(board[(i,j+4)])
                # For verticial value
                vCode = str(self.id) + str(board[(j,i)]) + str(board[(j+1,i)]) + str(board[(j+2,i)]) + str(board[(j+3,i)]) + str(board[(j+4,i)])
                
                if self.hValue.get(hCode) != None:
                    if hCode.count(color) > 0:
                        maxH = 10
                    maxH += (5 - self.hValue[hCode]) * 2
                if self.hValue.get(vCode) != None:
                    if vCode.count(color) > 0:
                        maxV = 10
                    maxV += (5 - self.hValue[vCode]) * 2
                maxQValue = max(maxQValue,maxH,maxV)
                
        for i in range(4, 11):
            if i == 6 or i == 7 or i == 8:
                 start, end = [0,7]
            if i == 4:
                start,end == [2,6]
            if i == 5:
                start,end = [1,7]
            if i == 9:
                start, end = [0,6]
            if i == 10:
                start, end = [1,5]
            for j in range (start, end):
                # for diagonal
                dCode = str(self.id) + str(board[(i,j)]) + str(board[(i-1,j+1)]) + str(board[(i-2,j+2)]) + str(board[(i-3,j+3)]) + str(board[(i-4,j+4)])
                
                if self.hValue.get(dCode) != None:
                    if dCode.count(color) > 0:
                        maxD = 10
                    maxD += (5 - self.hValue[dCode]) * 2
                maxQValue = max(maxQValue,maxD)
        
        return maxQValue
                
                        
    
                    