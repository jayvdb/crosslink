from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class LibravatarAccount(ServiceAccount):
    pass


class LibravatarIdentity(Identity):
    pass


class LibravatarService(Service):

    name = 'Libravatar'
    website = 'http://cdn.libravatar.org/'

    _url = website + 'avatar/{value}'

    _can_resolve = [GravatarMD5Hash]
    _can_verify = [GravatarMD5Hash]
    _account_cls = LibravatarAccount
    _identity_cls = LibravatarIdentity

    def create_identity(self, data):
        i = LibravatarIdentity(
             provider=self,
             identifier=data,
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, GravatarMD5Hash):
            url = self._url.format(value=fragment.value)
            data = fetch_head(url)

            if not data:
                return

            return self.create_identity(fragment)
