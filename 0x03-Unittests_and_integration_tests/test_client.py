#!/usr/bin/env python3

"""Unit tests for client module.

This module contains comprehensive unit tests for the client module,
specifically testing the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.
        
        This test ensures that:
        1. get_json is called once with the expected GitHub API URL
        2. The org property returns the value from get_json
        3. No external HTTP calls are made
        
        Args:
            org_name: The organization name to test with
            mock_get_json: The mocked get_json function
        """

        expected_org_data = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_org_data
        client = GithubOrgClient(org_name)
        result = client.org
        
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        self.assertEqual(result, expected_org_data)


if __name__ == '__main__':
    unittest.main()