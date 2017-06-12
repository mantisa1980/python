import json
cimport mymath
from mymath cimport my_add

TIMES = 1000000

cpdef test_loop():
    for i in xrange(TIMES):
        pass

cpdef test_loop2():
    cdef long int i=0
    for i in xrange(TIMES):
        pass

cpdef add(long i, long j):
    cdef long s = my_add(i,j)
    return s

cpdef test_json():
    for i in xrange(TIMES/10):
        in_data = json.dumps({"1":{"2":{"3":{"4":{"5":"ABC" } } } } })
        out_data = json.loads(in_data)

cpdef test_dict_access():
    in_data = {"1":{"2":{"3":{"4":{"5":"ABC" } } } } }
    for i in xrange(TIMES):
        y = in_data["1"]["2"]["3"]["4"]["5"]

cpdef test_dict_access2():
    cdef dict in_data = {"1":{"2":{"3":{"4":{"5":"ABC" } } } } }
    for i in xrange(TIMES):
        y = in_data["1"]["2"]["3"]["4"]["5"]

cpdef test_list():
    cdef list lst = []
    for i in xrange(TIMES):
        lst.append(i)

    for i in xrange(TIMES):
        y = lst[i]

cpdef test_addition():
    cdef int i = 0, j = 0
    for i in xrange(TIMES):
        j+=1

cpdef test_multiply():
    cdef int i = 0
    cdef long j
    for i in xrange(TIMES):
        j = i*i




cdef not_accessable_by_python(i):
    return i # cannot access

