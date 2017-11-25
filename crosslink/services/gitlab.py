from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class GitLabAccount(ServiceAccount):
    pass


class GitLabIdentity(Identity):

    def __init__(self, provider, identifier,
                 name,
                 preferred_username,
                 avatar_url,
                 extras=None,
                 ):
        super(GitLabIdentity, self).__init__(provider, identifier)
        self.name['formatted'] = name
        self.preferred_username = preferred_username

        self.extras = extras

        if avatar_url.startswith('https://secure.gravatar.com/avatar/'):
            gravatar_hash = avatar_url[len('https://secure.gravatar.com/avatar/'):]
            if '?' in gravatar_hash:
                gravatar_hash = gravatar_hash.split('?', 1)[0]

            account = Account('gravatar', GravatarMD5Hash(gravatar_hash))
            self.emails.append(VerifiedAccount(account, provider))


class GitLabService(Service):

    name = 'GitLab'
    website = 'https://gitlab.com/'

    _url = website + 'api/v4/users?search={value}'

    _can_resolve = [Email]
    _can_verify = [Email]
    _account_cls = GitLabAccount
    _identity_cls = GitLabIdentity

    def create_identity(self, data, extras=None):
        entry = data

        i = GitLabIdentity(
             provider=self, identifier=entry['id'],
             name=entry['name'],
             preferred_username=entry['username'],
             avatar_url=entry['avatar_url'],
             extras=extras,
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, Email):
            headers = {
                'Private-Token': self.token,
            }
            url = self._url.format(value=quote(str(fragment)))
            data = fetch_json(url, headers=headers)
            if not data:
                return

            assert isinstance(data, list)
            if len(data) == 0:
                return None
            assert len(data) == 1
            assert isinstance(data[0], dict)
            entry = data[0]

            extras = [VerifiedAccount(fragment, self)]

            return self.create_identity(entry, extras)
