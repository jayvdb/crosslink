import unittest

from crosslink import (
    Email,
    Account,
    Username,
    get_services,
    resolve,
    need,
)
from crosslink.services.keybase import (
    KeybaseAccount,
    KeybaseIdentity,
)


class TestKeybase(unittest.TestCase):

    def test_native_account_lookup(self):
        have = KeybaseAccount('Keybase', Username('jayvdb'))
        services = get_services('Keybase')
        results = resolve(have, services)
        print(results)
        assert results != [have]
        assert len(results) > 1

    def test_generic_account_lookup(self):
        have = Account('keybase', Username('jayvdb'))
        services = get_services('Keybase')
        results = resolve(have, services)
        assert results != [have]
        assert len(results) > 1

    def test_email_to_keybase(self):
        have = Email('jayvdb@gmail.com')
        services = get_services(['GitHub', 'Keybase'])
        result = need(have, KeybaseIdentity, services)
        assert result
