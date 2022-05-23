import time, random, heapq, re
from Yinsh.yinsh_model import YinshGameRule 
from copy import deepcopy
import json
import sys
sys.path.append('agents/t_080/')    ##append a path to sys to use externel file
from priorityQ import PriorityQueue



THINKTIME = 0.95

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        with open('agents/t_080/astar_hvalue.json', 'r',encoding='utf-8') as outfile:
            self.h = json.load(outfile)
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        
    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score > score      
    
    # Take a list of actions and an initial state, and perform astar search within a time limit.
    # Return the first action that leads to reward, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        P_queue = PriorityQueue()   ##openlist
        P_queue.push((deepcopy(rootstate), 0, []), 0)
        print(rootstate.board)
        # Conduct astar starting from rootstate.
        best_g = dict() #maps states to numbers
        counter = 0
        while not P_queue.isEmpty() and time.time()-start_time < THINKTIME:
            counter += 1
            state, gn, path = P_queue.pop() # Pop the next node (state, path) in the queue.
            num = board_to_num(state.board)
            #print(f"num is {num}")
            if (num not in best_g or (gn < best_g[num])):
                best_g[num] = gn
                new_actions = self.GetActions(state) # Obtain new actions available to the agent in this state.
                for a in new_actions: # Then, for each of these actions...
                    next_state = deepcopy(state)              # Copy the state.
                    next_path  = path + [a]                   # Add this action to the path.            
                    reward     = self.DoAction(next_state, a) # Carry out this action on the state, and note any reward.
                    if reward:
                        print(f"Move {len(next_path)}, path found:", next_path)
                
                        return next_path[0] # If this action was rewarded, return the initial action that led there.
                    else:
                        fn = gn + 1 + self.CalHeuristic(next_state.board)
                        P_queue.push((next_state, gn+1, next_path), fn)
        print(f"astar {counter}")
        return random.choice(actions) # If no reward was found in the time limit, return a random action.

    

    """ EMPTY    = 0
        RING_0   = 1
        CNTR_0   = 2
        RING_1   = 3
        CNTR_1   = 4
        ILLEGAL  = 5    """
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
                if self.h.get(h_code) != None:
                    if self.h.get(h_code) < min_h:
                        min_h = self.h.get(h_code)
                if self.h.get(v_code) != None:
                    if self.h.get(v_code) < min_v:
                        min_v = self.h.get(v_code)
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
                if self.h.get(z_code) != None:
                    if self.h.get(z_code) < min_z:
                        min_z = self.h[z_code]
        minimum = min(minimum, min_z)
        return minimum

##helper func
def board_to_num(board):
    list = board.tolist()
    num = []
    for i in list:
        num += i
    temp = [str(i) for i in num]
    num = int(''.join(temp))
    return num
