from service import Service

from openhub import OpenHubService
from gravatar import GravatarService
from libravatar import LibravatarService
from gitlab import GitLabService
from github import GitHubService
from keybase import KeybaseService


from identifiers import Email, GravatarMD5Hash


class OriginService(Service):

    name = 'origin'


class GravatarHashService(Service):

    _can_resolve = [Email]
    _account_cls = GravatarMD5Hash

    name = 'GravatarHash'

    def get_identity(self, fragment):
        if isinstance(fragment, Email):
            return GravatarMD5Hash.create(str(fragment))
