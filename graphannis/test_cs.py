import unittest

import sys
import os


from .cs import CorpusStorageManager
from .graph import GraphUpdate
from .util import node_name_from_match
import networkx as nx

class TestCorpusStorageManager(unittest.TestCase):
    def setUp(self):
        self.dataDir = os.path.normpath(os.path.realpath(__file__) + '/../../data')
        # load data if not test corpus does not exist yet
        relannis_dir = os.path.normpath(os.path.realpath(__file__) + '/../../relannis/GUM')
        if not os.path.isdir(self.dataDir + '/GUM' ) and os.path.isdir(relannis_dir):
            with CorpusStorageManager(self.dataDir) as cs:
                cs.import_from_fs(relannis_dir, corpus_name='GUM')
        
    def test_list(self):
        with CorpusStorageManager(self.dataDir) as cs:
            corpora = cs.list()
            assert(isinstance(corpora, list))

    def test_find(self):
        with CorpusStorageManager(self.dataDir) as cs:
            find_result = cs.find(['GUM'], 'pos="NN" . pos="NN"')
            assert(isinstance(find_result, list))

            assert(len(find_result) > 0)
            assert(isinstance(find_result[0], list))

            G = cs.subgraph('GUM', node_name_from_match(find_result[0]), 5, 5)
            assert(len(G.nodes) > 0)
            assert(len(G.edges) > 0)

    def test_subcorpus_graph(self):
        with CorpusStorageManager(self.dataDir) as cs:
            
            G = cs.subcorpus_graph('GUM', ['GUM/GUM_whow_skittles'])

            assert(len(G.nodes) > 0)
            assert(len(G.edges) > 0)

    def test_count(self):
        with CorpusStorageManager(self.dataDir) as cs:
            count_result = cs.count('GUM', 'pos="NN"')
            assert(isinstance(count_result, int))

            assert(count_result == 5688)

    def test_frequency(self):
        with CorpusStorageManager(self.dataDir) as cs:
            ft = cs.frequency('GUM', 'pos . pos', '1:pos,2:pos')
            
            assert(len(ft) > 0)
            assert(ft[0].count > 0)
            assert(type(ft[0].values) == list)
            assert(len(ft[0].values) == 2)
            assert(type(ft[0].values[0] == str))
            assert(type(ft[0].values[1] == str))


if __name__ == '__main__': unittest.main()
