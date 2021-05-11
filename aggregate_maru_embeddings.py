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

if __name__ == '__main__':
    #########################################
    #   Load arguments and configure file   #
    #########################################
    # Process CML arguments
    if len(sys.argv) < 1 + 2:
        print('--usage {} walk_file raw_emb'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(0)
    path_walk = sys.argv[1]
    path_raw_emb = sys.argv[2]
 
    # Count freq.
    subnodes = defaultdict(set)
    total = Counter() # total frequency for a parent node
    cnt = Counter() # frequency for subnodes
    with open(path_walk, 'r') as fp:
        for line in fp:
            data = line.strip().split(' ')
            for x in data:
                tp, nd, mp = x.split('_')
                nd, mp = int(nd), int(mp)
                subnodes[nd].add(x)
                total[nd] += 1
                cnt[x] += 1
    '''
    # Save your life with precomputed statistics.
    stat = pickle.load(open(path_walk + '.statistics', 'rb'))
    subnodes = stat['subnodes']
    cnt = stat['cnt']
    total = stat['total']
    '''

    print('{} parent nodes.'.format(len(subnodes), file=sys.stderr))
    # Load embeddings.
    raw_emb = {}
    emb_dim = -1
    with open(path_raw_emb, 'r') as fp:
        for line in fp:
            data = line.strip().split()
            if emb_dim < 0:
                emb_dim = int(data[1])
            else:
                raw_emb[data[0]] = np.array(list(map(float, data[1:])))
    
    # Aggregate embeddings.
    with open(path_raw_emb + '.final', 'w') as wp:
        print('{} {}'.format(len(subnodes), emb_dim), file=wp)
        for nd in subnodes:
            emb = np.zeros(emb_dim)
            for subnode in subnodes[nd]:
                emb += raw_emb[subnode] * cnt[subnode]
            emb /= float(total[nd])
            wp.write('{}'.format(nd))
            for i in range(emb_dim):
                wp.write(' {}'.format(emb[i]))
            wp.write('\n')

