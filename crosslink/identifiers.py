from utils import *


class Identifier(object):
    """A way to refer to an object on a service."""

    # Does it refer to a unique identifier
    _globally_unique = False
    # Can this identifier be re-used on many services
    _resuable = False

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return str(self)


class IntIdentifier(Identifier):
    pass


class Username(Identifier):
    _resuable = True


class Website(Identifier):
    _resuable = False


class Webpage(Identifier):
    _resuable = False
    _globally_unique = True


class HashedEmail(Identifier):
    _resuable = True
    _globally_unique = True


class GravatarMD5Hash(HashedEmail):

    @classmethod
    def create(cls, email):
        email = sanitize_email(email)
        hashed_email = md5_hash(email)
        return cls(hashed_email)


class EmailSHA1(HashedEmail):
    pass


class Account(object):
    """Information about an account."""
    def __init__(self, service_name, identifier):
        assert isinstance(identifier, Identifier)
        assert isinstance(service_name, str)
        if self.__class__.__name__ == 'Account':
            assert service_name == service_name.lower()
        else:
            assert service_name[0] == service_name[0].upper()

        self.service_name = service_name
        self.identifier = identifier

    def __str__(self):
        return '{} @ {}'.format(self.identifier, self.service_name)

    def __eq__(self, other):
        return str(self) == str(other)


class Email(Account):
    """Information about an account."""
    def __init__(self, email):
        # Prevent unicode on Python 2 to simplify supporting
        email = str(email)

        identifier, service_name = email.split('@', 1)
        identifier = Username(identifier)

        super(Email, self).__init__('@'+service_name, identifier)

    def __str__(self):
        return '%s%s' % (self.identifier, self.service_name)

    def __eq__(self, other):
        return str(self) == str(other)


class ServiceAccount(Account):
    """An account provided by a service."""
    _service = None

    def __init__(self, service_name, identifier):
        if not isinstance(service_name, str):
            service_name = service_name.name
        assert service_name[0] == service_name[0].upper()
        super(ServiceAccount, self).__init__(service_name, identifier)


class VerifiedAccount(object):
    """Information about an account that has been verified."""
    def __init__(self, account, verifier):
        assert isinstance(account, Account)
        # Should assert that verifier is a Service
        # but the requires circular imports
        assert not isinstance(verifier, str)
        self.account = account
        self.verifier = verifier

    def __str__(self):
        return '%s^%s' % (self.account, self.verifier)

    def __eq__(self, other):
        return str(self) == str(other)


class Identity(object):
    """Identity held by a service about an account."""

    _fragment_lists = ('emails', 'accounts', 'extras', 'ims', 'urls')

    def __init__(self, provider, identifier):
        if isinstance(identifier, int):
            identifier = IntIdentifier(identifier)
        elif not isinstance(identifier, Identifier):
            identifier = Username(identifier)

        self.account = provider._account_cls(provider.name, identifier)
        self.service = provider
        self.name = {
            'honorificPrefix': None,
            'givenName': None,
            'middleName': None,
            'familyName': None,
            'honorificSuffix': None,
            'formatted': None,
        }
        self.preferred_username = None
        self.display_name = None
        self.profile_url = None
        self.thumbnail_url = None
        self.current_location = None
        self.about_me = None
        self.note = None
        self.birthday = None
        self.gender = None
        self.utc_offset = None
        self.roles = []
        self.relationship = {
            'status': None,
            'interested_in': None,
        }
        self.emails = []
        self.extras = []
        self.accounts = []
        self.ims = []
        self.urls = []
        self.custom_data = None

    def __str__(self):
        return '%s(%s)' % (self.service.name, self.account.identifier)

    def get_fragments(self):
        yield VerifiedAccount(self.account, self.service)

        if self.preferred_username:
            cls = self.service._account_cls
            username = cls(self.service.name, Username(self.preferred_username))
            yield VerifiedAccount(username, self.service)

        for list_name in self._fragment_lists:
            items = getattr(self, list_name)
            if items is not None:
                for item in items:
                    yield item

    def __eq__(self, other):
        return str(self) == str(other)
