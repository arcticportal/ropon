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
