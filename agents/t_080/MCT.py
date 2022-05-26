import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque

THINKTIME = 0.95
g =0.6

class myAgent():
    def __init__(self, _id):
        self.id = _id  # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2)  # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score - score


    def SelectAction (self, actions, rootstate):
        start_time = time.time()
        V = dict()
        N = dict()
        string_root = re.sub(r'\D',"","".join(map(str,rootstate.board)))
        random_action = random.choice(actions)
        while time.time()-start_time < THINKTIME:
            state = deepcopy(rootstate)
            new_actions = actions
            currentState = string_root
            back = deque([(currentState)])
            reward = 0
            simulation = 0
            first_action = None

            while currentState in V and len(new_actions)>0 and reward ==0:
                if time.time()-start_time >= THINKTIME:
                    print("MCT", simulation)
                    return random_action

                cur_action = random.choice(new_actions)
                if not first_action :
                    first_action = cur_action
                next_state = deepcopy(state)
                reward = self.DoAction(next_state,cur_action)
                currentState = re.sub(r'\D',"","".join(map(str,next_state.board)))
                back.append(currentState)
                new_actions=self.GetActions(next_state)
                state =next_state

            if len(new_actions) > 0 and reward == 0:
                    while reward == 0 and len(new_actions)> 0 and simulation< 8:
                        if time.time()-start_time >= THINKTIME:
                            print("MCT", simulation)
                            return random_action

                        simulation += 1
                        cur_action = random.choice(new_actions)
                        next_state = deepcopy(state)
                        reward = self.DoAction(next_state,cur_action)
                        new_actions = self.GetActions(next_state)
                        state = next_state


            else :
                pass

            current_V = reward * (g **simulation)
            while len(back) and time.time()-start_time < THINKTIME:
                back_state = back.pop()

                if back_state in V:
                    if back_state == string_root and current_V > V[back_state]:
                        random_action =first_action
                        V[back_state] = max(V[back_state],current_V)
                        N[back_state] +=1
                else:
                    V[back_state] = current_V
                    N[back_state] =1

                current_V *= g

        return random_action
