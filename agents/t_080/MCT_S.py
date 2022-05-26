import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque

THINKTIME = 0.95
g =0.6

class obj():
    def __init__ (self,string_root,currentState,start_time,V,new_actions,reward,simulation,back,state,first_action,random_action) -> None:

        self.currentState = currentState
        self.start_time =start_time
        self.V= V
        self.new_actions = new_actions
        self.reward =reward
        self.simulation =simulation
        self.back = back
        self.state =state
        self.first_action= first_action
        self.random_action=random_action
        self.string_root =string_root



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


    def select(self,obj):
        while obj.currentState in obj.V and len(obj.new_actions) > 0 and obj.reward == 0:
            if time.time() - obj.start_time >= THINKTIME:
                print("MCT", obj.simulation)
                return obj.random_action

            cur_action = random.choice(obj.new_actions)
            if not obj.first_action:
                obj.first_action = cur_action
            next_state = deepcopy(obj.state)
            obj.reward = self.DoAction(next_state, cur_action)
            obj.currentState = re.sub(r'\D', "", "".join(map(str, next_state.board)))
            obj.back.append(obj.currentState)
            obj.new_actions = self.GetActions(next_state)
            obj.state = next_state



        return obj


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



            o = obj(currentState =currentState ,start_time= start_time,V=V,new_actions=new_actions,reward=reward,
                    string_root =string_root,simulation=simulation,back=back,state=state,first_action=first_action,random_action=random_action)

            o = self.select(o)



            new_actions = o.new_actions
            reward = o.reward
            back = o.back
            state = deepcopy(o.state)


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


            while o.currentState in  o.V or len(o.new_actions) < 0 or o.reward != 0:
             current_V = reward * (g ** simulation)
             while len(back) and time.time() - start_time < THINKTIME:
                back_state = back.pop()

                if back_state in V:
                    if back_state == string_root and current_V > V[back_state]:
                        random_action = first_action
                        V[back_state] = max(V[back_state], current_V)
                        N[back_state] += 1
                else:
                    V[back_state] = current_V
                    N[back_state] = 1

                current_V *= g

        return random_action
