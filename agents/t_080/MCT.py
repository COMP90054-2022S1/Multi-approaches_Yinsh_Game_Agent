import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque

THINKTIME = 0.95
gamma =0.6

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
        value = dict()
        node = dict()
        t_rootstate = re.sub(r'\D',"","".join(map(str,rootstate.board)))
        random_action = random.choice(actions)
        while time.time()-start_time < THINKTIME:
            state = deepcopy(rootstate)
            new_actions = actions
            t_cur_state = t_rootstate
            queue = deque([(t_cur_state)])
            reward = 0
            length = 0
            first_action = None

            while t_cur_state in value and len(new_actions)>0 and reward ==0:
                if time.time()-start_time >= THINKTIME:
                    print("mct", length)
                    return random_action

                cur_action = random.choice(new_actions)
                if not first_action :
                    first_action = cur_action
                next_state = deepcopy(state)
                reward = self.DoAction(next_state,cur_action)
                t_cur_state = re.sub(r'\D',"","".join(map(str,next_state.board)))
                queue.append(t_cur_state)
                new_actions=self.GetActions(next_state)
                state =next_state

            if len(new_actions) > 0 and reward == 0:
                    while reward == 0 and len(new_actions)> 0 and length< 10:
                        if time.time()-start_time >= THINKTIME:
                            print("mct", length)
                            return random_action

                        length += 1
                        cur_action = random.choice(new_actions)
                        next_state = deepcopy(state)
                        reward = self.DoAction(next_state,cur_action)
                        new_actions = self.GetActions(next_state)
                        state = next_state


            else :
                pass

            cur_value = reward * (gamma**length)
            while len(queue) and time.time()-start_time < THINKTIME:
                t_state = queue.pop()

                if t_state in value:
                    if t_state == t_rootstate and cur_value > value[t_state]:
                        random_action =first_action
                        value[t_state] = max(value[t_state],cur_value)
                        node[t_state] +=1
                else:
                    value[t_state] = cur_value
                    node[t_state] =1

                cur_value *= gamma
        print("mct", value)
        return random_action










import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque

THINKTIME = 0.95
gamma =0.6

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
        value = dict()
        node = dict()
        t_rootstate = re.sub(r'\D',"","".join(map(str,rootstate.board)))
        random_action = random.choice(actions)
        while time.time()-start_time < THINKTIME:
            state = deepcopy(rootstate)
            new_actions = actions
            t_cur_state = t_rootstate
            queue = deque([(t_cur_state)])
            reward = 0
            length = 0
            first_action = None

            while t_cur_state in value and len(new_actions)>0 and reward ==0:
                if time.time()-start_time >= THINKTIME:
                    print("mct", length)
                    return random_action

                cur_action = random.choice(new_actions)
                if not first_action :
                    first_action = cur_action
                next_state = deepcopy(state)
                reward = self.DoAction(next_state,cur_action)
                t_cur_state = re.sub(r'\D',"","".join(map(str,next_state.board)))
                queue.append(t_cur_state)
                new_actions=self.GetActions(next_state)
                state =next_state

            if len(new_actions) > 0 and reward == 0:
                    while reward == 0 and len(new_actions)> 0 and length< 10:
                        if time.time()-start_time >= THINKTIME:
                            print("mct", length)
                            return random_action

                        length += 1
                        cur_action = random.choice(new_actions)
                        next_state = deepcopy(state)
                        reward = self.DoAction(next_state,cur_action)
                        new_actions = self.GetActions(next_state)
                        state = next_state


            else :
                pass

            cur_value = reward * (gamma**length)
            while len(queue) and time.time()-start_time < THINKTIME:
                t_state = queue.pop()

                if t_state in value:
                    if t_state == t_rootstate and cur_value > value[t_state]:
                        random_action =first_action
                        value[t_state] = max(value[t_state],cur_value)
                        node[t_state] +=1
                else:
                    value[t_state] = cur_value
                    node[t_state] =1

                cur_value *= gamma
        print("mct", value)
        return random_action










import re
import time, random
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy
from collections import deque

THINKTIME = 0.95
gamma =0.6

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
        value = dict()
        N = dict()
        print(rootstate.board)
        state_to_string = re.sub(r'\D', "", "".join(map(str, rootstate.board)))
        random_action = random.choice(actions)
        while time.time() - start_time < THINKTIME:
            state = deepcopy(rootstate)
            new_actions = actions
            current_state = state_to_string
            BackPropagation = deque([(current_state)])
            reward = 0
            length = 0
            first_action = None

            while current_state in value:
              if len(new_actions) > 0 and reward == 0:

                cur_action = random.choice(new_actions)
                if not first_action:
                    first_action = cur_action
                next_state = deepcopy(state)
                reward = self.DoAction(next_state, cur_action)
                current_state = re.sub(r'\D', "", "".join(map(str, next_state.board)))
                BackPropagation.append(current_state)
                new_actions = self.GetActions(next_state)
                state = next_state


                if time.time() - start_time >= THINKTIME:
                    print("mct", length)
                    return random_action

              else :
                  return  random_action

            if len(new_actions) > 0 and reward == 0:
                while reward == 0 and len(new_actions) > 0 and length < 8:
                    if time.time() - start_time >= THINKTIME:
                        print("mct", length)
                        return random_action

                    length += 1
                    cur_action = random.choice(new_actions)
                    next_state = deepcopy(state)
                    reward = self.DoAction(next_state, cur_action)
                    new_actions = self.GetActions(next_state)
                    state = next_state

            else:
                pass

            cur_value = reward * (gamma ** length)
            while len(BackPropagation) and time.time() - start_time < THINKTIME:
                t_state = BackPropagation.pop()

                if t_state in value:
                    if t_state == state_to_string and cur_value > value[t_state]:
                        random_action = first_action
                        value[t_state] = max(value[t_state], cur_value)
                        N[t_state] += 1
                else:
                    value[t_state] = cur_value
                    N[t_state] = 1

                cur_value *= gamma
        print("mct", value)
        return random_action