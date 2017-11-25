from crosslink.service import Service

from crosslink.identifiers import Email, GravatarMD5Hash


class GravatarHashService(Service):

    name = 'GravatarHash'

    _can_resolve = [Email]
    _account_cls = GravatarMD5Hash

    def get_identity(self, fragment):
        if isinstance(fragment, Email):
            return self._account_cls.create(str(fragment))
