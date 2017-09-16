import numpy as np
from numpy import linalg as LA
from data import DATASET
import scipy
import time

DS = []

def preprocess():
    for i in DATASET:
        DS.append([float(j) for j in i])
    #print DS

def naive_cycle():
    update = 0
    w = w_old = np.array([.0,.0,.0,.0])
    found = False

    while True:
        #print "begin round : w=", w
        all_pass = True
        node = 0
        for i in DS:

            vxn = np.array(i[:4])
            yn = np.float(i[4])
            print "comparing node {} xn {} and wn {}".format(node, vxn, w)

            #inner_product = np.inner(w,vxn)
            inner_product = np.dot(w,vxn)
            
            if LA.norm(inner_product) == 0:
                print "inner product 0..."
                sign = -1
            else:
                sign = np.sign(inner_product)

            if sign != np.sign(yn):
                w_old = w
                w = w + yn * vxn
                #w = w/np.linalg.norm(w)
                print "sign mismatch(yn={},syn={},sign={},inner={}): xn={} wt={},node={},wt1={}".format(yn, np.sign(yn), sign, inner_product, vxn, w_old, node, w)
                all_pass = False
                raw_input("press to continue ....")
                update+=1
                if update % 10000 == 0:
                    print "sign mismatch(yn={},sign={}): vectors= {} and {},node={}, update={}".format(yn, sign, vxn, w, node, update)
                node = 0
                break

            else:
                node+=1

        if all_pass:
            print "found final w!", w
            break

def random_cycle():
    #print DS[0]
    update = 0
    w_old = np.array([0,0,0,0])
    w = np.array([0,0,0,0])
    found = False

    while True:
        #print "begin round : w=", w
        
        all_pass = True
        perm = np.random.permutation(len(DS))
        node = 0
        for j in perm:
            i = DS[j]
            vxn = np.array(i[:4])
            yn = i[4]

            inner_product = np.inner(w,vxn)
            
            if LA.norm(inner_product) == 0:
                print "inner product 0..."
                sign = -1
            else:
                sign = np.sign(inner_product)

            if sign != np.sign(yn):
                w_old = w
                w  = w + int(yn) * vxn
                print "sign mismatch(yn={},sign={}): xn={} wt={},node={},wt1={}".format(yn, sign, vxn, w_old, node, w)
                all_pass = False
                raw_input("press to continue ....")
                update+=1
                if update % 10000 == 0:
                    print "sign mismatch(yn={},sign={}): vectors= {} and {},node={}, update={}".format(yn, sign, vxn, w, node, update)

                break
            else:
                node+=1

        if all_pass:
            print "found final w!", w
            break


preprocess()
naive_cycle()
#random_cycle()



