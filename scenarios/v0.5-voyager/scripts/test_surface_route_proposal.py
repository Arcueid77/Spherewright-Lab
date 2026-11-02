import math
import unittest
from surface_route_proposal import Projection,route

class RouteProposalTests(unittest.TestCase):
    def test_short_detour_ends_in_interaction_region(self):
        r=route((90,0),[(8,-8,18,8)],goal_radius=55)
        self.assertFalse(r['executable']);self.assertFalse(r['nativePathClearance'])
        self.assertTrue(any(abs(y)>8 for x,y in r['points']))
        x,y=r['points'][-1];self.assertLessEqual(math.hypot(90-x,y),55)
    def test_projection_roundtrip(self):
        p=Projection((0,0,200));q=p.surface((20,10));x,y=p.project(q)
        self.assertAlmostEqual(20,x);self.assertAlmostEqual(10,y)
    def test_full_barrier_does_not_become_clear(self):
        with self.assertRaises(ValueError):route((90,0),[(4,-100,80,100)],goal_radius=10)
    def test_large_or_malformed_requests_reject(self):
        with self.assertRaises(ValueError):route((2000,0),[],goal_radius=10)
        with self.assertRaises(ValueError):route((90,0),[(5,0,1,2)])

if __name__=='__main__':unittest.main()
