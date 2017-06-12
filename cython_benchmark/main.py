import time
import json
import mylib
import timeit
import sys

TIMES = 1000000

def measure_time(fn):
    def decorator(*args, **kwargs):
        t = time.time()
        r1 = fn(*args, **kwargs)
        r2 = time.time()-t
        if len(args) == 0:
            print "elapsed time of {}:{}".format( fn, r2)
        else:
            print "elapsed time of {}:{}, ratio={}".format( fn, r2, args[0]/r2 )
        return r2
    return decorator

@measure_time
def test_loop(base_t=None):
    j = 0
    for i in xrange(TIMES):
        j+=1
    return j

@measure_time
def ctest_loop(base_t=None):
    mylib.test_loop()

@measure_time
def ctest_loop2(base_t=None):
    mylib.test_loop2()


@measure_time
def ctest_json(base_t=None):
    mylib.test_json()

@measure_time
def test_json(base_t=None):
    for i in xrange(TIMES/10):
        in_data = json.dumps({"1":{"2":{"3":{"4":{"5":"ABC" } } } } })
        out_data = json.loads(in_data)

@measure_time
def test_dict_access(base_t=None):
    in_data = {"1":{"2":{"3":{"4":{"5":"ABC" } } } } }
    for i in xrange(TIMES):
        y = in_data["1"]["2"]["3"]["4"]["5"]

@measure_time
def ctest_dict_access(base_t=None):
    mylib.test_dict_access()

@measure_time
def ctest_dict_access2(base_t=None):
    mylib.test_dict_access2()

@measure_time
def test_list(base_t=None):
    lst = []
    for i in xrange(TIMES):
        lst.append(i)

    for i in xrange(TIMES):
        y = lst[i]

@measure_time
def test_addition(base_t=None):
    i = j = 0
    for i in xrange(TIMES):
        j+=1

@measure_time
def ctest_addition(base_t=None):
    mylib.test_addition()

@measure_time
def ctest_list(base_t=None):
    mylib.test_list()

@measure_time
def test_multiply():
    i = 0
    j = 0
    for i in xrange(TIMES):
        j = i*i

@measure_time
def ctest_multiply(base_t=None):
    mylib.test_multiply()

@measure_time
def ctest_list(base_t=None):
    mylib.test_list()

if __name__ == "__main__":
    t = test_loop()
    ctest_loop(t)
    ctest_loop(t)
    
    t = test_addition()
    ctest_addition(t)

    t = test_list()
    ctest_list(t)

    t = test_dict_access()
    ctest_dict_access(t)
    ctest_dict_access2(t)

    t = test_json()
    ctest_json(t)

    t = test_multiply()
    ctest_multiply(t)


 

