#!/usr/bin/env python3
# generate_incetare.py - Generator acte incetare CIM
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_docs import gen_incetare

data = json.loads(sys.argv[1])
result = gen_incetare(data['angajat'], data['extra'])
sys.stdout.buffer.write(result)
