# -*- coding: utf-8 -*-
import subprocess
output = subprocess.check_output('ls', shell=True)
print(output)

if 4 > 2 > 1:
    print "111"