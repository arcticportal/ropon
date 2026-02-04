from django.test import TestCase
from django.core.exceptions import ValidationError
from ropon_data.blocks import SOSOBoundingBoxBlock

class SOSOBoundingBoxBlockTests(TestCase):
    def test_valid_soso_bounding_box_block(self):
        block = SOSOBoundingBoxBlock()
        value = block.clean({
            'southwest': {
                'latitude': -60.0,
                'longitude': -180.0
            },
            'northeast': {
                'latitude': 60.0,
                'longitude': 180.0
            }
        })
        self.assertEqual(value['southwest']['latitude'], -60.0)
        self.assertEqual(value['northeast']['latitude'], 60.0)

    def test_invalid_coordinate_ranges(self):
        """Test all invalid coordinate boundary conditions in a single parameterized test"""
        block = SOSOBoundingBoxBlock()
        
        # Test cases: (corner, coord_type, invalid_value)
        invalid_cases = [
            # Southwest latitude violations
            ('southwest', 'latitude', -91.0),
            ('southwest', 'latitude', 91.0),
            # Southwest longitude violations  
            ('southwest', 'longitude', -181.0),
            ('southwest', 'longitude', 181.0),
            # Northeast latitude violations
            ('northeast', 'latitude', -91.0),
            ('northeast', 'latitude', 91.0),
            # Northeast longitude violations
            ('northeast', 'longitude', -181.0),
            ('northeast', 'longitude', 181.0),
        ]
        
        for corner, coord_type, invalid_value in invalid_cases:
            with self.subTest(corner=corner, coord_type=coord_type, value=invalid_value):
                test_data = {
                    'southwest': {'latitude': -60.0, 'longitude': -180.0},
                    'northeast': {'latitude': 60.0, 'longitude': 180.0}
                }
                test_data[corner][coord_type] = invalid_value
                
                with self.assertRaises(ValidationError):
                    block.clean(test_data)

    def test_invalid_northeast_south_of_southwest(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': 0.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': -1.0,  # invalid - north less than south
                    'longitude': 180.0
                }
            })

    def test_soso_bounding_box_is_not_a_verticle_line(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': 0.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 0.0,
                    'longitude': 180.0
                }
            })

    def test_soso_bounding_box_is_not_a_horizontal_line(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': 0.0
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 0.0
                }
            })
