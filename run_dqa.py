#!/usr/bin/env python3
import sys
try:
    sys.argv[1]
except:     
    print('Please indicate which folder contains the DQA data?\ne.g. "run_DQA ~/DATA/test7"')
    exit()

print({})
from DQA_test import run_DQA as dqa
dqa.run_tests(sys.argv[1])
