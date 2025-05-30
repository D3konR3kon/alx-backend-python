#!/usr/bin/env python3

"""Unit tests for client module.

This module contains comprehensive unit tests for the client module,
specifically testing the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, PropertyMock
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

    def test_public_repos_url(self):
        """Test that GithubOrgClient._public_repos_url returns the expected URL.
        
        This test ensures that:
        1. The _public_repos_url property returns the correct repos_url from org data
        2. The org property is properly mocked to return known payload
        3. The URL construction is correct based on the mocked org data
        """

        known_payload = {
            "login": "test-org",
            "id": 12345,
            "repos_url": "https://api.github.com/orgs/test-org/repos"
        }
        
        with patch.object(
            GithubOrgClient, 
            'org', 
            new_callable=PropertyMock
        ) as mock_org:

            mock_org.return_value = known_payload

            client = GithubOrgClient("test-org")
            result = client._public_repos_url
 
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that GithubOrgClient.public_repos returns the expected list of repos.
        
        This test ensures that:
        1. get_json is called once with the mocked _public_repos_url
        2. The public_repos method returns the expected list of repository names
        3. Both the mocked property and get_json are called exactly once
        
        Args:
            mock_get_json: The mocked get_json function
        """

        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        
        mock_get_json.return_value = test_payload

        test_repos_url = "https://api.github.com/orgs/test-org/repos"
        
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:

            mock_public_repos_url.return_value = test_repos_url
            client = GithubOrgClient("test-org")
            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]

            self.assertEqual(result, expected_repos)

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_repos_url)


if __name__ == '__main__':
    unittest.main()