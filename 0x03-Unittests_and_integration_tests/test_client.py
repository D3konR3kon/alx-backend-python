#!/usr/bin/env python3

"""Unit tests for client module.

This module contains comprehensive unit tests for the client module,
specifically testing the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that GithubOrgClient.has_license returns the correct boolean value.

        This test ensures that:
        1. has_license correctly identifies when a repo has the specified license
        2. has_license returns False when the repo has a different license
        3. The method handles different license key comparisons correctly

        Args:
            repo: The repository dictionary with license information
            license_key: The license key to check for
            expected: The expected boolean result
        """

        client = GithubOrgClient("test-org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient.

    This class tests the integration of GithubOrgClient methods while only
    mocking external HTTP requests. It uses fixtures to provide realistic
    test data and ensures the client works correctly end-to-end.
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures and start patching requests.get.

        This method:
        1. Starts a patcher for requests.get
        2. Configures the mock to return appropriate fixtures based on URL
        3. Sets up the side_effect to handle different API endpoints
        """
        def requests_get_side_effect(url):
            """Side effect function to return appropriate fixtures based on URL.

            Args:
                url: The URL being requested

            Returns:
                Mock response object with json() method
            """
            mock_response = Mock()

            if url.endswith("/orgs/google"):
                mock_response.json.return_value = cls.org_payload
 
            elif "/repos" in url:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}

            return mock_response

        cls.get_patcher = patch('requests.get')
        cls.mock_requests_get = cls.get_patcher.start()

        cls.mock_requests_get.side_effect = requests_get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures and stop patching.

        This method stops the requests.get patcher to ensure clean test
        environment and prevent side effects on other tests.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that GithubOrgClient.public_repos returns expected results.

        This integration test ensures that:
        1. The public_repos method returns the correct list of repository names
        2. The method works end-to-end with mocked HTTP requests
        3. The result matches the expected_repos from fixtures
        """

        client = GithubOrgClient("google")

        result = client.public_repos()

        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test GithubOrgClient.public_repos with license="apache-2.0".

        This integration test ensures that:
        1. The public_repos method correctly filters by license
        2. Only repositories with apache-2.0 license are returned
        3. The result matches the apache2_repos from fixtures
        """

        client = GithubOrgClient("google")

        result = client.public_repos(license="apache-2.0")

        self.assertEqual(result, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()