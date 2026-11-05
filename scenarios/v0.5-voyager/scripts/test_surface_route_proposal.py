import math
import unittest
from surface_route_proposal import Projection,route,spherical_candidates,WaypointNetwork

class RouteProposalTests(unittest.TestCase):
    def test_coarse_network_can_first_move_away_from_goal_without_claiming_clearance(self):
        start=(0,0,200);goal=(10,0,200)
        network=WaypointNetwork([(0,4,200),(5,4,200),(10,4,200),goal],goal,maximum_step=5.1,goal_radius=1)
        rows=network.candidates(start,minimum_step=1)
        self.assertEqual((0,4,200),rows[0]['position'])
        self.assertGreater(math.dist(rows[0]['position'],goal),math.dist(start,goal))
        self.assertEqual(14,rows[0]['remainingGeometricCost'])
        self.assertFalse(rows[0]['executable']);self.assertFalse(rows[0]['nativePathClearance']);self.assertFalse(rows[0]['terrainVerified'])
    def test_disconnected_observations_do_not_invent_a_corridor(self):
        network=WaypointNetwork([(0,0,200),(20,0,200)],(20,0,200),maximum_step=5,goal_radius=1)
        self.assertEqual([],network.candidates((0,0,200),minimum_step=1))
    def test_waypoint_requests_remain_finite_and_bounded(self):
        with self.assertRaises(ValueError):WaypointNetwork([(float('nan'),0,200)],(0,0,200))
        with self.assertRaises(ValueError):WaypointNetwork([(0,0,200)]*8193,(0,0,200))
        with self.assertRaises(ValueError):WaypointNetwork([(0,0,200)],(0,0,200),maximum_step=65)
        network=WaypointNetwork([(0,0,200)],(0,0,200))
        with self.assertRaises(ValueError):network.candidates((0,float('inf'),200))
    def test_global_hemisphere_approach_keeps_radius_and_never_claims_native_clearance(self):
        rows=spherical_candidates((0,0,200),(0,150,-132.2875656))
        self.assertEqual(7,len(rows))
        for row in rows:
            self.assertAlmostEqual(200,math.sqrt(sum(v*v for v in row['position'])))
            self.assertLessEqual(row['arcMetres'],40)
            self.assertFalse(row['executable']);self.assertFalse(row['nativePathClearance']);self.assertFalse(row['terrainVerified'])
        self.assertLess(rows[0]['goalDistance'],math.dist((0,0,200),(0,150,-132.2875656)))
    def test_short_detour_ends_in_interaction_region(self):
        r=route((90,0),[(8,-8,18,8)],goal_radius=55)
        self.assertFalse(r['executable']);self.assertFalse(r['nativePathClearance'])
        self.assertTrue(any(abs(y)>8 for x,y in r['points']))
        x,y=r['points'][-1];self.assertLessEqual(math.hypot(90-x,y),55)
    def test_projection_roundtrip(self):
        p=Projection((0,0,200));q=p.surface((20,10));x,y=p.project(q)
        self.assertAlmostEqual(20,x);self.assertAlmostEqual(10,y)
    def test_overlapping_start_enclosures_are_not_erased(self):
        a=(-7.1,-3.6,1,4.6);b=(-.1,-1.4,6.3,5)
        r=route((70,70),[a,b],goal_radius=50);x,y=r['points'][0]
        self.assertTrue(r['escapeConservativeEnclosures'])
        self.assertEqual(0,x)
        self.assertTrue(y>8 or y<-6)
        self.assertFalse(r['nativePathClearance'])
    def test_full_barrier_does_not_become_clear(self):
        with self.assertRaises(ValueError):route((90,0),[(4,-100,80,100)],goal_radius=10)
    def test_large_or_malformed_requests_reject(self):
        with self.assertRaises(ValueError):route((2000,0),[],goal_radius=10)
        with self.assertRaises(ValueError):route((90,0),[(5,0,1,2)])

if __name__=='__main__':unittest.main()
