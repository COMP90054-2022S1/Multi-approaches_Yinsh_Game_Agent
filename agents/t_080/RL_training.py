# -*- coding: utf-8 -*-
"""
Created on Sun May 22 14:13:24 2022

@author: pc-user
"""

import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
import sys
sys.path.append('agents/t_080/')
import json

THINKTIME = 0.95
diagPoint = [(0,0),(0,0),(0,0),(0,0),(2,6),(1,7),(0,7),(0,7),(0,7),(0,6),(1,5)]
epsi = 0.4
alpha = 0.1
gamma = 0.9

# Define agent
class myAgent:
    def __init__(self,_id):
        self.id = _id                     # Remember agent id
        self.game_rule = YinshGameRule(2) # Number of agents
        
        self.weight = [0,0,0,0]
        self.round = 0
        
        with open('agents/t_080/astar_hvalue.json', 'r', encoding = 'utf-8') as fw:
            self.hValue = json.load(fw)
            
        """with open("agent/t_080/RL_weight.json", 'r', encoding = 'utf-8') as fw:
            self.weight = json.load(fw)['weight']"""
        
    
    # Generate action from this state
    def GetActions(self, state):
        return self.game_rule.getLegalAction(state,self.id)
    
    
    # Carry out a given action on this state and return True if reward received
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score - score
    
    
    def CalRemainStepsFeature(self,board):
        self_ring_color = str(2 * (self.id + 1) - 1)
        max_value = 0
        
        for i in range(1,10):
            start = max(0, 5-i)
            end = min(7, 12-i)
            for j in range(start, end):
                horizontial = str(self.id) + str(board[(i,j)]) + str(board[(i,j+1)]) + str(board[(i,j+2)]) + str(board[(i,j+3)]) + str(board[(i,j+4)])
                vertical = str(self.id) + str(board[(j,i)]) + str(board[(j+1,i)]) + str(board[(j+2,i)]) + str(board[(j+3,i)]) + str(board[(j+4,i)])
                value1 = 0
                value2 = 0
                
                if horizontial in self.hValue:
                    if horizontial.count(self_ring_color) > 0:
                        value1 = 10
                    value1 += (5-self.hValue[horizontial]) * 2
                
                if vertical in self.hValue:
                    if vertical.count(self_ring_color) > 0:
                        value2 = 10
                    value2 += (5 - self.hValue[vertical]) * 2
                
                max_value = max(max_value, value1, value2)
        
        for i in range(4,11):
            start,end = diagPoint[i]
            for j in range(start, end):
                diagonal = str(self.id) + str(board[(i,j)]) + str(board[(i-1,j+1)]) + str(board[(i-2,j+2)]) + str(board[(i-3,j+3)]) + str(board[(i-4,j+4)])
                value3 = 0
                
                if diagonal in self.hValue:
                    if diagonal.count(self_ring_color) > 0:
                        value3 = 10
                    value3 += (5 - self.hValue[diagonal]) * 2
                max_value = max(max_value,value3)
                 
        return max_value
    
    
    def CalFeatures(self,state,action):
        self_counter_color = 2 * (self.id + 1)
        oppo_counter_color = 2 * ((1-self.id) + 1)
        features = []
        
        # Score
        next_state = deepcopy(state)
        score = self.DoAction(next_state, action)
        features.append(score/3)
        
        # Self counter
        t_board = "".join(map(str,next_state.board))
        features.append(t_board.count(str(self_counter_color))/51)
        
        # Oppo counter
        features.append(t_board.count(str(oppo_counter_color))/51)
        
        # Remain step
        features.append(self.CalRemainStepsFeature(next_state.board)/21)
        
        return features
    
    
    def CalQValue(self,state,action,actions):
        features = self.CalFeatures(state, action, actions)
        
        if len(features) != self.weight:
            print("Feature and weight length are not matching")
            return -999
        else:
            ans = 0
            for i in range(len(features)):
                ans += features[i] * self.weight[i]
            return ans
        
    
    def SelectAction(self,actions,rootstate):
        self.round += 1
        start_time = time.time()
        best_Q_value = -999
        best_action = random.choice(actions)
        
        if self.round <= 5:
            return best_action
        else:
            pass
        
        if random.uniform(0, 1) < 1 - epsi:
            for action in actions:
                if time.time() - start_time > THINKTIME:
                    print('TIME OUT')
                    break
                
                Q_value = self.CalQValue(deepcopy(rootstate), action)
                
                if Q_value > best_Q_value:
                    best_Q_value = Q_value
                    best_action = action
        
        else:
            Q_value = self.CalQValue(deepcopy(rootstate), best_action)
            best_Q_value = Q_value
            
        next_state = (deepcopy(rootstate))
        reward = self.Doaction(next_state,best_action)
        
        next_actions = self.GetActions(next_state)
        best_next_Q_value = -999
        
        for action in next_actions:
            if time.time() - start_time > THINKTIME:
                print("TIME OUT")
                break
            
            Q_value = self.CalQValue(deepcopy(rootstate), action)
            best_next_Q_value = max(best_next_Q_value,Q_value)
            
        features = self.CalFeatures(deepcopy(rootstate), best_action)
        delta_value = reward + gamma * best_next_Q_value - best_Q_value
        
        for i in range(len(features)):
            self.weight[i] += alpha * delta_value * features[i]
            
        with open('agants/t_080/RL_weight.json','w',encoding='utf-8') as fw:
            json.dump({"weight":self.weight}, fw, index = 4, ensure_ascii=False)
        
        print("TIME: ", time.time() - start_time)
        return best_action
        