# -*- coding: utf-8 -*-
import time

def get_host(key,nodes):
    
    host = nodes[0]
    for i in nodes:
        if key < i[1]:
            return i[0]
    return host[0]

d = dict()

nodes =[("v1",10), ("v2",20),("v3",30),("v4",40),("v5",50) ]

for i in range(0,50):
    host = get_host(i,nodes)
    print i, host
    if host not in d:
        d[host]=0
    d[host]+=1
print d


d = dict()
nodes =[("v1",10), ("v2",20),("v4",40),("v5",50) ]
for i in range(0,50):
    host = get_host(i,nodes)
    print i, host
    if host not in d:
        d[host]=0
    d[host]+=1
print d

##
