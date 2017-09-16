import numpy as np
from numpy import linalg as LA
from data import DATASET as DS
import scipy
import matplotlib.pyplot as plt


def draw_new_round(wt1, wt):
    # n vectors with origin X[n],Y[n] , X magnitude U[n] , Y magnitude V[n]
    X = [0,0]
    Y = [0,0]
    U = [wt1[0], wt[0]]
    V = [wt1[1], wt[1]]
        
    XT = [0]
    YT = [0]
    UT = [wt1[1]]
    VT = [-wt1[0]]
    print "wt=", U[0],V[0], ", wvert=", UT,VT
    ax = plt.gca()
    ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color=['red', 'blue'])
    plt.draw()
    ax.quiver(XT,YT, UT, VT, angles='xy', scale_units='xy', scale=1, color=['yellow'])
    plt.draw()
    #ax.set_xlim([-10, 10])
    #ax.set_ylim([-10, 10])
    plt.show()

def _draw_source_data():
    positive_data = []
    negative_data = []
    for i in DS:
        if i[2] > 0:
            positive_data.append(i[:2])
        else:
            negative_data.append(i[:2])
        #dot_data.append(i[:2])
    
    ax = plt.gca()
    ax.plot(*zip(*positive_data), marker='o', color='g', ls='')
    ax.plot(*zip(*negative_data), marker='o', color='r', ls='')
    ax.set_xlim([-20, 20])
    ax.set_ylim([-20, 20])
    plt.draw()

def draw(wt1, wt):
    _draw_source_data()
    draw_new_round(wt1, wt)

def main():
    #print DS[0]
    w_old = np.array([0,0])
    w = np.array([0,0])
    found = False

    while True:
        print "begin round : w=", w
        
        draw(w, w_old)
        all_pass = True

        node = 0
        for i in DS:
            vxn = np.array(i[:2])
            yn = i[2]
            inner_product = np.inner(w,vxn)
            
            if LA.norm(inner_product) == 0:
                print "inner product 0..."
                sign = -1
            else:
                sign = np.sign(inner_product)

            if sign != yn:
                print "sign mismatch(yn={},sign={}): vectors= {} and {},node={}".format(yn, sign, vxn, w, node)
                w_old = w
                w  = w + yn*vxn
                all_pass = False
                #raw_input("press to continue ....")
                break
            else:
                node+=1

        if all_pass:
            print "found final w!", w
            draw(w, w_old)
            break

main()
#test()
#test_plot_dot()