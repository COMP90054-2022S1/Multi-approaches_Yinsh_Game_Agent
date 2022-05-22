####
"""This file is used to generate a json file for the H value search
for astar search"""
####
import json

#input a 6-digit num string to generate the movement need to generate a sequence in 5
def H_generator(seq):
    if seq[0] == 0: #player 1
        ring, mark = 1, 2
        opring, opmark = 3, 4
        ans = H_logic(ring,mark,opring,opmark,seq)
    else:   #player2
        ring, mark = 3, 4
        opring, opmark = 1, 2
        ans = H_logic(ring,mark,opring,opmark,seq)
    return ans


def H_logic(ring,mark,opring,opmark,seq):
    ##if have opponent ring, cant make a sequence
    ans = 0
    seq = seq[1:]
    if seq.count(opring) > 0:
        return 999
    if seq.count(0) == 5:
        return 6
    if seq.count(opmark) == 0:  #if no opmark 
        ans = seq.count(0) + seq.count(ring)
    else:   #have opmark
        ##add num of ring and empty
        ans = seq.count(0) + seq.count(ring) + seq.count(opmark)
        ##consider of the possible of continous opmark
        counter = check_continous_opmark(seq,opmark)
        if counter > 1 and counter < 4:
            if seq.count(ring) != 0:
                ans -= check_continous_opmark(seq,opmark)
        if counter > 3 :
            if seq.count(ring) != 0:
                ans = 1
            else:
                ans = 2 
    return ans

##count countinous opmark number
def check_continous_opmark(seq,opmark):
    counter1 = 1
    # looping till length - 2
    i = 0
    while i < len(seq)-1:
    
        # checking the conditions
        if seq[i] == opmark:
            if i != len(seq) -2:
                for i1 in range (i+1 ,len(seq)):
                    if seq[i1] == opmark:
                        counter1 += 1
                    else:
                        i = i1 + 1
                        break
        i += 1
    return counter1

if __name__ == '__main__':
    ##first digit represent player , p1 is 0 and p2 is 1
    result = {}
    for i1 in range (0,2):
        #then followed by 5 digits reperesent 5 continous positions
        for i2 in range (0,5):
            for i3 in range (0,5):
                for i4 in range (0,5):
                    for i5 in range (0,5):
                        for i6 in range (0,5):
                            seq = [i1,i2,i3,i4,i5,i6]
                            val = H_generator(seq)
                            Str = "".join([str(_) for _ in seq])
                            result.update({Str : val})
                            
#convert result into json and write into externel file in same dict
with open('astar_hvalue.json', 'w',encoding='utf-8') as outfile:
    json.dump(result, outfile,indent = 4)


