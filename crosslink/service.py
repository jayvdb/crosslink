"""Service stub."""

from crosslink.identifiers import Account, Identity


class Service(object):

    name = None
    website = None

    _can_resolve = []
    _can_verify = []
    _account_cls = Account
    _identity_cls = Identity

    def __init__(self, token=None):
        self.token = token

    def get_identity(self, fragment):
        pass

    def __str__(self):
        return '%s' % self.name
