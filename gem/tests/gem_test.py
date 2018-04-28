
# coding: utf-8

# In[1]:

import unittest
import gem
from gem import transit
from copy import deepcopy
from gem.sample_data import *


def hashDigraph(digraph):
    
    return (tuple(sorted(digraph.nodes())), tuple(sorted(digraph.edges())))

digraph = gem.convertToGraph(test_schedule)

class TestMethods(unittest.TestCase):
    
    def test_convertToGraph(self):
        self.assertEqual(hashDigraph(digraph), (test_digraph_nodes, test_digraph_edges))
    
    def test_pathing(self):
        D = deepcopy(digraph)
        self.assertEqual(transit.traverseGraph('A', 'C', 0, D), 1600)
        
    def test_elapsed(self):
        
        self.assertEqual(transit.getElapsed(100, 1200), 1100)
        self.assertEqual(transit.getElapsed(10070, 100), 110)
        
    def test_validations(self):
        self.assertEqual(transit.validate_point(digraph, 'A'), 'A')
        self.assertEqual(transit.validate_time(999),999)
        
    def test_augment_graph(self):
        D = deepcopy(digraph)
        transit.augmentDigraph(D, 'A', 'E', 100)
        self.assertEqual('Origin' in D.nodes(), True)
        self.assertEqual('Destination' in D.nodes(), True)
        
    def test_getMatrix(self):
        self.assertEqual(sorted(transit.getTransitMatrix(digraph)), test_matrix)
        
    

if __name__ == '__main__':
    
    unittest.main()
