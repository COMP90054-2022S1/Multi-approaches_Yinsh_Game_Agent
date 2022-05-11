# INFORMATION ------------------------------------------------------------------------------------------------------- #


# Author:  Steven Spratley
# Date:    04/01/2021
# Purpose: Implements an example breadth-first search agent for the COMP90054 competitive game environment.


# IMPORTS AND CONSTANTS ----------------------------------------------------------------------------------------------#


import time, random, heapq, re
from Yinsh.yinsh_model import YinshGameRule 
from copy import deepcopy
import sys
sys.path.append('agents/t_080/')
import json

THINKTIME = 0.85
diagPoints = [(0,0),(0,0),(0,0),(0,0),(2,6),(1,7),(0,7),(0,7),(0,7),(0,6),(1,5)]

# FUNCTIONS ----------------------------------------------------------------------------------------------------------#

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.
        with open("agents/t_080/astar_util.json", 'r', encoding='utf-8') as fw:
            self.hValue = json.load(fw)

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score > score      
    
    def CalHeuristic(self, board):
        min_value = 51
        for i in range(1, 10):
            start = max(0, 5-i)
            end = min(7, 12-i)
            for j in range(start, end):
                horizontal = str(self.id) + str(board[(i,j)]) + str(board[(i,j+1)]) + str(board[(i,j+2)]) + str(board[(i,j+3)]) + str(board[(i,j+4)])
                vertical = str(self.id) + str(board[(j,i)]) + str(board[(j+1,i)]) + str(board[(j+2,i)]) + str(board[(j+3,i)]) + str(board[(j+4,i)])
                value1 = 51
                value2 = 51
                if horizontal in self.hValue:
                    value1 = self.hValue[horizontal]
                if vertical in self.hValue:
                    value2 = self.hValue[vertical]
                min_value = min(min_value, value1, value2)

        for i in range(4, 11):
            start, end = diagPoints[i]
            for j in range (start, end):
                diagonal = str(self.id) + str(board[(i,j)]) + str(board[(i-1,j+1)]) + str(board[(i-2,j+2)]) + str(board[(i-3,j+3)]) + str(board[(i-4,j+4)])
                value3 = 51
                if diagonal in self.hValue:
                    value3 = self.hValue[diagonal]
                min_value = min(min_value, value3)
        return min_value
    
    # Take a list of actions and an initial state, and perform breadth-first search within a time limit.
    # Return the first action that leads to reward, if any was found.
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        queue = PriorityQueue()
        queue.push((deepcopy(rootstate), 0, []), 0)
        # Conduct BFS starting from rootstate.
        best_g = dict()
        while not queue.isEmpty() and time.time()-start_time < THINKTIME:
            state, gn, path = queue.pop() # Pop the next node (state, path) in the queue.
            key = re.sub(r'\D', "", "".join(map(str,state.board)))
            if (key not in best_g or (gn < best_g[key])):
                best_g[key] = gn
                new_actions = self.GetActions(state) # Obtain new actions available to the agent in this state.
                for a in new_actions: # Then, for each of these actions...
                    next_state = deepcopy(state)              # Copy the state.
                    next_path  = path + [a]                   # Add this action to the path.            
                    reward     = self.DoAction(next_state, a) # Carry out this action on the state, and note any reward.
                    if reward:
                        print(f"Move {len(next_path)}, path found:", next_path)
                
                        return next_path[0] # If this action was rewarded, return the initial action that led there.
                    else:
                        queue.push((next_state, gn+1, next_path), gn+1+self.CalHeuristic(next_state.board)) # Else, simply add this state and its path to the queue.
        return random.choice(actions) # If no reward was found in the time limit, return a random action.
        
    
# END FILE -----------------------------------------------------------------------------------------------------------#
