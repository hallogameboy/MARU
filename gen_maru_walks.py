#!/usr/bin/env python3
import data_helpers
from scipy import spatial
from collections import defaultdict, Counter, deque
import scipy.sparse as sp

def cosine_sim(__x, __y):
    return 1.0  - spatial.distance.cosine(__x, __y)

from scipy.stats import spearmanr

import pickle

import numpy as np
import yaml, time, datetime
import os, sys, random

try:
    import ujson as json
except:
    print('Cannot import ujson, import json instead.', file=sys.stderr)
    import json
try:
    from smart_open import smart_open as open
except:
    print('smart_open inexists, use the original open instead.', file=sys.stderr)


def gen_mp_candidates(edges, node_type, num_samples, window_size):
    mpset = set()
    for i in edges:
        for j in range(num_samples):
            cur_path = deque([node_type[i]])
            cur_node = i
            for k in range(window_size):
                cur_node = random.choice(edges[cur_node])
                cur_path.append(node_type[cur_node])
            cur_node = i
            for k in range(window_size):
                cur_node = random.choice(edges[cur_node])
                cur_path.appendleft(node_type[cur_node])
            mpset.add(''.join(list(cur_path)))
    mp_idx = {k : j + 1 for j, k in enumerate(sorted(list(mpset)))}
    return mp_idx

def maru_walk(start, walk_len, window_size, edges, node_type, type_idx, mp_idx, types, wp):
    node_path = deque([start])
    type_path = deque([node_type[start]]) 
    cur = start
    for i in range(walk_len + window_size):
        cur = random.choice(edges[cur])
        node_path.append(cur)
        type_path.append(node_type[cur])
    cur = start
    for i in range(walk_len + window_size):
        cur = random.choice(edges[cur])
        node_path.appendleft(cur)
        type_path.appendleft(node_type[cur])
    
    node_path = list(node_path)
    type_path = list(type_path)
    
    ret = []
    for i in range(window_size, len(node_path)):
        if i + window_size >= len(node_path): break
        mp = ''.join(type_path[i - window_size:i + window_size + 1])
        assert(len(mp) == 2 * window_size + 1)
        mp = mp_idx[mp] if mp in mp_idx else 0
        try:
            tp = types[type_idx[type_path[i]]]
        except:
            print(type_path[i], type_idx[type_path[i]])


        ret.append('{}_{}_{}'.format(tp, node_path[i], mp))
    assert(len(ret) == 2 * walk_len + 1)
    print(' '.join(ret), file=wp)



if __name__ == '__main__':

    #########################################
    #   Load arguments and configure file   #
    #########################################
    # Process CML arguments
    if len(sys.argv) < 1 + 4:
        print('--usage {} walk_len window_size num_walks_per_node dataset'.format(sys.argv[0]), file=sys.stderr)
        print('Note that walk_len and window_size are both for one side.', file=sys.stderr)
        sys.exit(0)

    walk_len = int(sys.argv[1])
    window_size = int(sys.argv[2])
    num_walks_per_node = int(sys.argv[3])
    dataset = sys.argv[4]
    assert(walk_len > 0)
    assert(window_size > 0)


    print('walk_len = ', walk_len)
    print('window_size = ', window_size)
    print('num_walks_per_node = ', num_walks_per_node)

    # Load the config file 
    cfg = yaml.load(open('config.yml', 'r'))

    #########################################
    #   Set up random seeds                 #
    #########################################
    random.seed(252)
    np.random.seed(252)

    #########################################
    #  Load graph data                      #
    #########################################
    num_nodes, num_edges, node_list, edges, node_type, type_idx = data_helpers.load_dataset(cfg['path_data'], dataset)

    mp_idx = gen_mp_candidates(edges, node_type, 10, window_size)
    print('{} different metapaths.'.format(len(mp_idx)), file=sys.stderr)
    # print(mp_idx)
    num_metapaths = len(mp_idx) + 1
    types = ['v', 'a', 'i', 'f']
    
    #########################################
    #  MARU walks                           #
    #########################################
    out_file = cfg['path_walks'] + 'maru_walks.{}.L{}.W{}.S{}'.format(dataset, walk_len, window_size, num_walks_per_node)
    with open(out_file, 'w') as wp:
        for walk_itr in range(num_walks_per_node):
            print('Iteration #{}'.format(walk_itr), file=sys.stderr)
            random.shuffle(node_list)
            for start in node_list:
                maru_walk(start, walk_len, window_size, edges, node_type, type_idx, mp_idx, types, wp)
