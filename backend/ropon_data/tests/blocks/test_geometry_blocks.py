from django.test import TestCase
from django.core.exceptions import ValidationError
from ropon_data.blocks import SOSOBoundingBoxBlock, BoundingBoxBlock

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

    def test_invalid_southwest_latitude_negative(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -91.0,  # invalid
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 180.0
                }
            })

    def test_invalid_southwest_latitude_positive(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': 91.0,  # invalid
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 180.0
                }
            })

    def test_invalid_southwest_longitude_negative(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': -181.0  # invalid
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 180.0
                }
            })

    def test_invalid_southwest_longitude_positive(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': 181.0  # invalid
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 180.0
                }
            })

    def test_invalid_northeast_latitude_negative(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': -91.0,  # invalid
                    'longitude': 180.0
                }
            })

    def test_invalid_northeast_latitude_positive(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 91.0,  # invalid
                    'longitude': 180.0
                }
            })

    def test_invalid_northeast_longitude_negative(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': -181.0  # invalid
                }
            })

    def test_invalid_northeast_longitude_positive(self):
        block = SOSOBoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'southwest': {
                    'latitude': -60.0,
                    'longitude': -180.0
                },
                'northeast': {
                    'latitude': 60.0,
                    'longitude': 181.0  # invalid
                }
            })

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

class BoundingBoxBlockTests(TestCase):
    def test_valid_bounding_box_block(self):
        block = BoundingBoxBlock()
        value = block.clean({
            'south': -60.0,
            'west': -180.0,
            'north': 60.0,
            'east': 180.0,
        })
        self.assertEqual(value, {
            'south': -60.0,
            'west': -180.0,
            'north': 60.0,
            'east': 180.0,
        })
        
    def test_invalid_bounding_box_block_north_less_than_south(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': 60.0,
                'west': 180.0,
                'north': 50.0, # invalid
                'east': -180.0,
            })
        
    def test_invalid_bounding_box_block_south_out_of_range_negative(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -91.0, # invalid
                'west': -180.0,
                'north': 60.0,
                'east': 180.0,
            })
    
    def test_invalid_bounding_box_block_west_out_of_range_negative(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': -181.0, # invalid
                'north': 60.0,
                'east': 180.0,
            })

    def test_invalid_bounding_box_block_north_out_of_range_negative(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': -180.0,
                'north': -91.0, # invalid
                'east': 180.0,
            })
    
    def test_invalid_bounding_box_block_east_out_of_range_negative(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': -180.0,
                'north': 60.0,
                'east': -181.0, # invalid
            })

    def test_invalid_bounding_box_block_south_out_of_range_positive(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': 91.0,  # invalid
                'west': -180.0,
                'north': 60.0,
                'east': 180.0,
            })
    
    def test_invalid_bounding_box_block_west_out_of_range_positive(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': 181.0,  # invalid
                'north': 60.0,
                'east': 180.0,
            })
    
    def test_invalid_bounding_box_block_north_out_of_range_positive(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': -180.0,
                'north': 91.0,  # invalid
                'east': 180.0,
            })
    
    def test_invalid_bounding_box_block_east_out_of_range_positive(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': -180.0,
                'north': 60.0,
                'east': 181.0,  # invalid
            })

    def test_bounding_box_block_is_not_a_vertical_line(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': -60.0,
                'west': 0.0,
                'north': 60.0,
                'east': 0.0,
            })

    def test_bounding_box_block_is_not_a_horizontal_line(self):
        block = BoundingBoxBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'south': 0.0,
                'west': -180.0,
                'north': 0.0,
                'east': 180.0,
            })