import unittest

from geometry_request import complete_geometry_arrays


class GeometryRequestTests(unittest.TestCase):
    def test_object_only_cut_sends_empty_terrain_array(self):
        self.assertEqual(complete_geometry_arrays({'objectIds': [7]}),
                         {'objectIds': [7], 'terrainPoints': []})

    def test_terrain_only_cut_sends_empty_object_array(self):
        point = {'x': 200, 'y': 0, 'z': 0}
        self.assertEqual(complete_geometry_arrays({'terrainPoints': [point]}),
                         {'objectIds': [], 'terrainPoints': [point]})

    def test_layout_binding_and_native_segments_are_preserved(self):
        request = {'expectedFactoryGeometryHash': 'existing-layout', 'nativeBeltSegments': [{'routingMode': 'native_grid'}]}
        result = complete_geometry_arrays(request)
        self.assertEqual(result['expectedFactoryGeometryHash'], request['expectedFactoryGeometryHash'])
        self.assertEqual(result['nativeBeltSegments'], request['nativeBeltSegments'])

    def test_prepared_caller_packet_is_not_mutated(self):
        original = {'objectIds': [7]}
        result = complete_geometry_arrays(original)
        result['objectIds'].append(8)
        self.assertEqual(original, {'objectIds': [7]})

    def test_explicit_null_or_wrong_collection_type_stays_an_error(self):
        for value in (None, {}, '7'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                complete_geometry_arrays({'objectIds': value, 'terrainPoints': []})

    def test_empty_cut_is_rejected_before_game_start(self):
        with self.assertRaises(ValueError):
            complete_geometry_arrays({})


if __name__ == '__main__':
    unittest.main()
