#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from parameterized import parameterized
from utils import access_nested_map, get_json

class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function."""

    @parameterized.expand([
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns expected results."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)

class TestGetJson(unittest.TestCase):
    """Test class for get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test that get_json returns expected results and calls requests.get."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response
        
        result = get_json(test_url)
        
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)

           
if __name__ == "__main__":
    unittest.main()