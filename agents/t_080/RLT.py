import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
import sys
sys.path.append('agent/t_080/')
import json

THINKTIME = 0.95
episodes = 0.5
alpha = 0.2
gamma = 0.8


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
    
    
    """# Fundamental action function for select each action in different rounds
    def SelectAction(self,actions,rootstate):
        start_time = time.time()
        self.round += 1
        best_Q = -99999
        bestAction = random.choice(actions)
        #if self.round <= 5:
        #    return bestAction
        for action in actions:
            Q_value = self.CalQValue(deepcopy(rootstate),action)
            if Q_value > best_Q:
                best_Q = Q_value
                bestAction = action
        return bestAction"""

    #cal Q value 
    def CalQValue(self,state,action):
        features = []
        #ring num of player
        if self.id == 0 : selfmark = str(2) ; oppomark = str(4)
        else: selfring =  selfmark = str(4) ; oppomark = str(2)
        #normalize and append into featuresList
        features = []
        next_state = deepcopy(state)
        num = str(board_to_num(next_state.board))
        #F1 score
        score_diff = self.DoAction(next_state,action)
        features.append(score_diff/3)
        #F2 self counter
        features.append(num.count(str(selfmark))/51)
        #F3 oppo counter
        features.append(num.count(str(oppomark))/51)
        #F4 remain steps
        features.append(self.VariationH(next_state.board)/26)
        if len(features) != len(self.weight):
            raise Exception(f"feature in dem {len(features)} , weight in dem {len(self.weight)}")
        result = 0
        for i in range (len(features)):
            result += features[i] *self.weight[i]
        return result
    
    
    """ EMPTY    = 0
        RING_0   = 1
        CNTR_0   = 2
        RING_1   = 3
        CNTR_1   = 4
        ILLEGAL  = 5    """
    def VariationH(self,board):
        maximum = -999
        for i in range(1, 10):  #only loop row 1 - 9
            start = max(0, 5-i)
            end = min(7, 12-i)
            if i == 5:
                start = 1
                end = 6
            for j in range (start,end):
                h_code = str(self.id) + str(board[(i,j)]) + str(board[(i,j+1)]) + str(board[(i,j+2)]) + \
                    str(board[(i,j+3)]) + str(board[(i,j+4)])
                v_code = str(self.id) + str(board[(j,i)]) + str(board[(j+1,i)]) + str(board[(j+2,i)]) + \
                    str(board[(j+3,i)]) + str(board[(j+4,i)])

                #if have our ring, make it important
                if self.hValue.get(h_code) != None or self.hValue.get(v_code):
                    h = Algorithom_booster(self.hValue,self.id,h_code)
                    v = Algorithom_booster(self.hValue,self.id,v_code)
                    maximum = max(maximum, h, v)

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
            for j in range (start,end):
                d_code = str(self.id) + str(board[(i,j)]) + str(board[(i-1,j+1)]) + str(board[(i-2,j+2)]) + \
                    str(board[(i-3,j+3)]) + str(board[(i-4,j+4)])
                if self.hValue.get(d_code) != None:
                    maximum = max(maximum,Algorithom_booster(self.hValue,self.id,d_code))
        return maximum

    def DefineFeatures(self,state, action):
        features = []
        #ring num of player
        if self.id == 0 : selfmark = str(2) ; oppomark = str(4)
        else: selfring =  selfmark = str(4) ; oppomark = str(2)
        #normalize and append into featuresList
        next_state = deepcopy(state)
        num = str(board_to_num(next_state.board))
        #F1 score
        score_diff = self.DoAction(next_state,action)
        features.append(score_diff/3)
        #F2 self counter
        features.append(num.count(str(selfmark))/51)
        #F3 oppo counter
        features.append(num.count(str(oppomark))/51)
        #F4 remain steps
        features.append(self.VariationH(next_state.board)/26)
        return features
    
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
        # The first five steps apply random action
        """if self.round < 6:
            return initialAction
        else:"""
        # e-greedy
        if random.uniform(0, 1) <= episodes:
            for action in actions:
                if time.time() - startTime >THINKTIME:
                    print("TIME OUT")
                    #break
                else:
                    # Calculate Q-value
                    QValue = self.CalQValue(deepcopy(pState),action)
                    # Change best Q-value to max Q-value
                    # Change best action from random to the current action
                    if QValue > bestQValue:
                        bestQValue = QValue
                        bestAction = action
        else:
            QValue = self.CalQValue(deepcopy(pState), bestAction)
            bestQValue = QValue
        
        nextState = (deepcopy(pState))
        reward = self.DoAction(nextState,bestAction)
        nextAction = self.GetActions(nextState)
        
        bestNextQ = -999
        for nAction in nextAction:
            if time.time() - startTime > THINKTIME:
                print("TIME OUT")
            else:
                QValue = self.CalQValue(deepcopy(nextState), nAction)
                bestNextQ = max(bestNextQ,QValue)
                
        features = self.DefineFeatures(deepcopy(pState), bestAction)
        
        delta = reward + gamma * bestNextQ - bestQValue
        
        for i in range(len(features)):
            self.weight[i] += alpha * delta * features[i]
            
        with open("agents/t_080/weight.json", 'w', encoding='utf-8') as wList:
            json.dump({"weight": self.weight}, wList, indent = 4, ensure_ascii = False)
        print(f"(weight : {self.weight})")
        return bestAction
            
#extra weight on sequence with ring
def Algorithom_booster(hValue,selfid,code):
        #ring num of player
        if selfid == 0 : selfring = str(1) ; opporing = str(3) ; selfmark = str(2) ; oppomark = str(4)
        else: selfring = str(3) ; opporing = str(1) ; selfmark = str(4) ; oppomark = str(2)
        num = (6 - hValue[code])
        #if have our ring, make it important
        if code.count(selfring) > 0:
            if code.count(selfmark) == 2:
                num += 5
            if code.count(selfmark) >= 3:
                num += 10
        #if have 1 or more opporing and  2 or more their marker:
        if code.count(oppomark) > 3:
            num += 10
        return num

##helper func
def board_to_num(board):
    list = board.tolist()
    num = []
    for i in list:
        num += i
    temp = [str(i) for i in num]
    num = int(''.join(temp))
    return num
    
    