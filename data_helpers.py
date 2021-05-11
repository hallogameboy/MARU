#!/usr/bin/env python3
import sys, os
import numpy as np
import scipy.sparse as sp
import pickle
import math
from collections import defaultdict, Counter
try:
    import ujson as json
except:
    print('Cannot import ujson, import json instead.', file=sys.stderr)
    import json

try:
    from smart_open import smart_open as open
except:
    print('smart_open inexists, use original one instead.', file=sys.stderr)
    
import random

def load_dataset(path_data, dataset):
    
    # Read edges.
    mx_node = 0
    edges = defaultdict(list)
    num_edges = 0
    node_set = set()
    with open(path_data + dataset + '.edges', 'r') as fp:
        for line in fp:
            a, b = map(int, line.split())
            edges[a].append(b)
            edges[b].append(a)
            num_edges += 1
            node_set.add(a)
            node_set.add(b)
    
    node_list = sorted(list(node_set))
    num_nodes = len(node_list)

    # Read node types.
    node_type = pickle.load(open(path_data + dataset + '.type', 'rb'))
    type_idx = {j: i for i, j in enumerate(sorted(list(set(node_type))))}

    return num_nodes, num_edges, node_list, edges, node_type, type_idx

def load_lp_dataset(path_data, dataset):
    
    # Read edges.
    mx_node = 0
    edges = defaultdict(list)
    num_edges = 0
    node_set = set()
    with open(path_data + dataset + '.edges.lp.train', 'r') as fp:
        for line in fp:
            a, b = map(int, line.split())
            edges[a].append(b)
            edges[b].append(a)
            num_edges += 1
            node_set.add(a)
            node_set.add(b)
    
    node_list = sorted(list(node_set))
    num_nodes = len(node_list)

    # Read node types.
    node_type = pickle.load(open(path_data + dataset + '.type', 'rb'))
    type_idx = {j: i for i, j in enumerate(sorted(list(set(node_type))))}

    return num_nodes, num_edges, node_list, edges, node_type, type_idx

