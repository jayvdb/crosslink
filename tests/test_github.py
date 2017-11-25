import unittest

from crosslink import (
    Email,
    get_services,
    resolve,
    need,
)
from crosslink.services.github import (
    GitHubAccount,
    GitHubIdentity,
)


class TestGitHub(unittest.TestCase):

    def test_email_lookup(self):
        have = Email('jayvdb@gmail.com')
        services = get_services('GitHub')
        results = resolve(have, services)
        assert results
        assert len(results) >= 1

    def test_email_to_account(self):
        have = Email('jayvdb@gmail.com')
        services = get_services('GitHub')
        result = need(have, GitHubAccount, services)
        assert result

    def t2est_email_to_identity(self):
        have = Email('jayvdb@gmail.com')
        services = get_services('GitHub')
        result = need(have, GitHubIdentity, services)
        assert result

    def test_email_to_any(self):
        have = Email('jayvdb@gmail.com')
        services = get_services('GitHub')
        result = need(have, (GitHubAccount, GitHubIdentity), services)
        assert result
