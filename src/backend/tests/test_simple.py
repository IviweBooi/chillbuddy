#!/usr/bin/env python3
"""
Simple test to verify testing framework is working
"""

import unittest
from .test_config import BaseTestCase


class TestSimple(BaseTestCase):
    """Simple test class to verify testing framework"""
    
    def test_basic_math(self):
        """Test basic math operations"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(3 * 3, 9)
        self.assertTrue(5 > 3)
    
    def test_string_operations(self):
        """Test string operations"""
        test_string = "Hello World"
        self.assertEqual(test_string.lower(), "hello world")
        self.assertTrue("World" in test_string)
        self.assertEqual(len(test_string), 11)
    
    def test_list_operations(self):
        """Test list operations"""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(test_list), 5)
        self.assertIn(3, test_list)
        self.assertEqual(test_list[0], 1)
        self.assertEqual(test_list[-1], 5)


if __name__ == '__main__':
    unittest.main()