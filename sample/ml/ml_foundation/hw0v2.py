import numpy as np
from numpy import linalg as LA
from data import DATASET
import scipy
import time

DS = []
DIMENSION = 5

def preprocess():
    for i in DATASET:
        i.insert(0,1) # insert 1 at beginning for threshold. I don't know why without it the program will not halt.
        DS.append([float(j) for j in i])
    #print DS

def naive_cycle():
    w = w_old = np.array([.0 for i in xrange(DIMENSION)])
    correct_num = 0
    rounds = 0

    while correct_num < len(DS):
        node = 0
        for i in DS:
            vxn = np.array(i[:DIMENSION])
            yn = np.float(i[DIMENSION])
            inner_product = np.dot(w,vxn)
   
            if LA.norm(inner_product) == 0:
                sign = -1
            else:
                sign = np.sign(inner_product)

            print "comparing node {} xn {} and wn {}:INP={},Sign(INP)={}".format(node, vxn, w, inner_product, sign)

            if sign != np.sign(yn):
                rounds +=1
                correct_num = 0
                w_old = w
                w = w + yn * vxn
                print "wrong(yn={},syn={},sign={},inner={}):xn={},wt={},node={},wt1={},next rounds={}".format(yn, np.sign(yn), sign, inner_product, vxn, w_old, node, w, rounds)
            else:
                correct_num+=1
                if correct_num == len(DS):
                    print "done, rounds={}, w={}".format(rounds, w)
                    break
            node+=1

def random_cycle(scale=1):
    experiments = 0.0
    total_rounds = 0.0
    while experiments < 2000:
        print "experiments", experiments
        correct_num = 0
        rounds = 0
        w = w_old = np.array([.0 for i in xrange(DIMENSION)])
        perm = np.random.permutation(len(DS))
        while correct_num < len(DS):
            node = 0
            for j in perm:
                i = DS[j]
                vxn = np.array(i[:DIMENSION])
                yn = np.float(i[DIMENSION])
                inner_product = np.dot(w,vxn)
       
                if LA.norm(inner_product) == 0:
                    sign = -1
                else:
                    sign = np.sign(inner_product)

                #print "comparing node {} xn {} and wn {}:INP={},Sign(INP)={}".format(node, vxn, w, inner_product, sign)

                if sign != np.sign(yn):
                    rounds +=1
                    correct_num = 0
                    w_old = w
                    w = w + yn * vxn * scale
                    #print "wrong(yn={},syn={},sign={},inner={}):xn={},wt={},node={},wt1={},next rounds={}".format(yn, np.sign(yn), sign, inner_product, vxn, w_old, node, w, rounds)
                else:
                    correct_num+=1
                    if correct_num == len(DS):
                        print "done, rounds={}, w={}".format(rounds, w)
                        experiments += 1
                        total_rounds+=rounds
                        break
                node+=1
        
    print "total rounds={}, avg rounds={}".format(total_rounds, total_rounds/experiments)




preprocess()
#naive_cycle()
random_cycle(0.5)



