import scipy
import numpy as np
import matplotlib.pyplot as plt

def plot_vector():
    #soa = np.array([[0, 0, 3, 2], [0, 0, 1, 1], [0, 0, 9, 9]])
    #print soa
    #X, Y, U, V = zip(*soa)
    #print X,Y,U,V
    X = [0,0,0]
    Y = [0,0,0]
    U = [3,1,9]
    V = [2,1,9]
    # n vectors with origin X[n],Y[n] , X magnitude U[n] , Y magnitude V[n]
    plt.figure()
    ax = plt.gca()
    ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color=['blue', 'red', 'black'])
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    #plt.draw()
    plt.show()
    print "done"


def plot_sin():
    import matplotlib.pyplot as plt
    x = np.arange(0.,10.,0.1)
    y = np.sin(x)
    f1 = plt.figure()
    f11 = f1.add_subplot("111")
    plt.plot(x,y)

    #f2 = plt.figure()
    a = np.arange(5)
    b = np.exp(a)
    #f2 = plt.plot(a,b)
    #f11.plot(a,b)
    plt.plot(a,b)

    plt.show()
    

def multi_img():
    DataRange = range(0, 360)
    DataRange = map(scipy.deg2rad, DataRange)
    Data1 = map(scipy.sin, DataRange)
    Data2 = map(scipy.cos, DataRange)

    plt.subplot(211)
    plt.plot(Data1)
    plt.subplot(212)
    plt.plot(Data2)
    plt.show()



'''
x = np.arange(5)
y = np.exp(x)
fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.plot(x, y)

z = np.sin(x)
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.plot(x, z)

'''
plot_vector()
#plot_sin()
#multi_img()