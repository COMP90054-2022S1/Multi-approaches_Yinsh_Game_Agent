from concurrent.futures.process import _MAX_WINDOWS_WORKERS
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
import sys
sys.path.append('agents/t_080/')
import json

THINKTIME = 0.9

class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        
        self.weight = [1,0.1,-0.1,0.2]
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
    def SelectAction(self,actions,rootstate):
        print(f"counter left {rootstate.counters_left}")
        start_time = time.time()
        self.round += 1
        best_Q = -99999
        bestAction = random.choice(actions)
        """##play strategy at first 5 rings position
        if self.round <= 5:
            return self.RingStrategy(actions,rootstate, self.round)"""

        ##block oppo when they hValue == 1 when self hValue >1
        h = self.cal_H_for_both(rootstate)
        print(f"is {h[1]} == 1? is {h[0]} > 1")
        if self.diffScore(rootstate)[2] <= 1 and rootstate.counters_left <= 25:   
          if h[1] == 1 and h[0] > 1:
              print("block?!")
              ans = self.blockOppo(rootstate,actions)
              if ans != None: 
                  return ans
        while time.time()-start_time < THINKTIME:
            for action in actions:
                Q_value = self.CalQValue(deepcopy(rootstate),action)
                if Q_value > best_Q:
                    best_Q = Q_value
                    bestAction = action
            return bestAction
        return random.choice(actions)

    def blockOppo(self,rootstate,actions):
        min_self_next_h = 999
        max_oppo_next_h = 1
        for action in actions:
            next_state = deepcopy(rootstate)
            self.DoAction(next_state,action)
            self_next_h = self.CalHeuristic(next_state.board)
            self.id= 1 - self.id
            oppo_next_h = self.CalHeuristic(next_state.board)
            self.id= 1 - self.id
            if oppo_next_h >= max_oppo_next_h:
                if self_next_h <= min_self_next_h:
                    max_oppo_next_h = oppo_next_h
                    min_self_next_h = self_next_h
                    bestAction = action
        if min_self_next_h == 999:  #did not found a result
            return None
        """if max_oppo_next_h == 1:    #cant stop
            print("cant stop")
            return None"""
        print("block!!")
        return bestAction

    def cal_H_for_both(self,rootstate):   #calculate h value for both
        hself = self.CalHeuristic(rootstate.board)
        self.id= 1 - self.id
        hoppo = self.CalHeuristic(rootstate.board)
        self.id= 1 - self.id
        return [hself,hoppo]

    
    def RingStrategy (self,actions,rootstate, round):
        if self.id == 0 : oppoid = 1
        else: oppoid = 0
        centralP = (5,5)    #central position in board
        oppoRs = rootstate.ring_pos[oppoid] ##opponant rings positions
        bestAction = random.choice(actions)
        #if we r first player, put first ring always at the centtal pt
        if self.id == 0 and round == 1:
            bestAction['place pos'] = centralP
            return bestAction
        min_disR = 999
        min_disC = 999
        for x in range (0,11):
            for y in range (0,11):
                if rootstate.board[(x,y)] == 0:
                    for oppoR in oppoRs:
                        disR = Caldis((x,y),oppoR)
                        disC = Caldis((x,y),centralP)
                        #depend on disR first, then disC
                        if disR <= min_disR:
                            if disC < min_disC:
                                min_disC = disC
                                min_disR = disR
                                bestAction['place pos'] = (x,y)
        return bestAction

    #cal Q value 
    def CalQValue(self,state,action):
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
        features.append(self.VariationH(next_state.board)/16)
        if len(features) != len(self.weight):
            raise Exception(f"feature in dem {len(features)} , weight in dem {len(self.weight)}")
        result = 0
        for i in range (len(features)):
            result += features[i] *self.weight[i]
        return result
    
    #return a list of [self score, opponent socre, advantage by self - oppo ]
    def diffScore (self,state):
        selfscore = state.agents[self.id].score
        self.id= 1 - self.id
        opposcore = state.agents[self.id].score
        self.id= 1 - self.id
        return [selfscore,opposcore,selfscore-opposcore]
    
    
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

    """To simplify the calculation processs, use hard code to avoid unnacessary loop in the board"""
    """If there are less than 4 elements in a row which are not number 5, then skip it"""
    def CalHeuristic(self, board):
        #search_list = [[4, 7], [3, 7], [2, 7], [1, 7], [1, 6], [0, 6], [0, 5], [0, 4], [0, 3]]
        #diagPoints = [(2,6),(1,7),(0,7),(0,7),(0,7),(0,6),(1,5)]
        min_h = min_v = min_z= 999
        for i in range(1, 10):  #only loop row 1 - 9
            start = max(0, 5-i)
            end = min(7, 12-i)
            if i == 5:
                start = 1
                end = 6
            for j in range(start, end):
                #6 digits code, fisrt place means player no. last 5 digits means sequence
                h_code = str(self.id) + str(board[(i,j)]) + str(board[(i,j+1)]) + str(board[(i,j+2)]) + \
                    str(board[(i,j+3)]) + str(board[(i,j+4)])
                v_code = str(self.id) + str(board[(j,i)]) + str(board[(j+1,i)]) + str(board[(j+2,i)]) + \
                    str(board[(j+3,i)]) + str(board[(j+4,i)])
                #find min value in externel h value list by using code
                if self.hValue.get(h_code) != None:
                    if self.hValue.get(h_code) < min_h:
                        min_h = self.hValue.get(h_code)
                if self.hValue.get(v_code) != None:
                    if self.hValue.get(v_code) < min_v:
                        min_v = self.hValue.get(v_code)
        minimum = min(min_h,min_v)

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
                z_code = str(self.id) + str(board[(i,j)]) + str(board[(i-1,j+1)]) + str(board[(i-2,j+2)]) + \
                    str(board[(i-3,j+3)]) + str(board[(i-4,j+4)])
                if self.hValue.get(z_code) != None:
                    if self.hValue.get(z_code) < min_z:
                        min_z = self.hValue[z_code]
        minimum = min(minimum, min_z)
        return minimum

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
        """#if have 1 or more opporing and  2 or more their marker:
        if code.count(oppomark) > 3:
            num += 10"""
        return num

##helper func
#transfer board in list into str
def board_to_num(board):
    list = board.tolist()
    num = []
    for i in list:
        num += i
    temp = [str(i) for i in num]
    num = int(''.join(temp))
    return num

#calculate steps between dots in board
def Caldis(selfPos, oppoPos):
    xDiff = selfPos[0] - oppoPos[0]
    yDiff = selfPos[1] - oppoPos[1]
    if xDiff * yDiff > 0:
        diff = max(abs(xDiff),abs(yDiff))
    else:
       diff = abs(xDiff) + abs(yDiff)
    return diff