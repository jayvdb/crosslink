from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class GitHubAccount(ServiceAccount):
    pass


class GitHubIdentity(Identity):

    def __init__(self, provider, identifier,
                 preferred_username,
                 gravatar_id,
                 avatar_url,
                 extras=None,
                 ):
        super(GitHubIdentity, self).__init__(provider, identifier)
        self.preferred_username = preferred_username

        if gravatar_id:
            assert False

        if 'githubusercontent.com' not in avatar_url and identifier not in avatar_url:
            assert False

        self.extras = extras

        if avatar_url.startswith('https://secure.gravatar.com/avatar/'):
            gravatar_hash = avatar_url[len('https://secure.gravatar.com/avatar/'):]
            if '?' in gravatar_hash:
                gravatar_hash = gravatar_hash.split('?', 1)[0]

            self.emails.append(GravatarMD5Hash(gravatar_hash))


class GitHubService(Service):

    name = 'GitHub'
    website = 'https://github.com/'

    _url = 'https://api.github.com/search/users?q={value}'

    _can_resolve = [Email]
    _can_verify = [Email]
    _account_cls = GitHubAccount
    _identity_cls = GitHubIdentity

    def create_identity(self, data, extras=None):
        entry = data

        assert entry['type'] == 'User'

        i = GitHubIdentity(
             provider=self, identifier=entry['id'],
             preferred_username=entry['login'],
             gravatar_id=entry['gravatar_id'],
             avatar_url=entry['avatar_url'],
             extras=extras,
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, Email):
            url = self._url.format(value=quote(str(fragment)))
            data = fetch_json(url, auth=self.token)

            assert isinstance(data, dict)

            if 'total_count' not in data:
                return None
            if data['total_count'] != 1:
                return None
            if 'items' not in data:
                return None

            assert isinstance(data['items'], list)
            assert len(data['items']) == 1
            assert isinstance(data['items'][0], dict)
            entry = data['items'][0]

            extras = [VerifiedAccount(fragment, self)]

            return self.create_identity(entry, extras)

        elif isinstance(fragment, (GitHubAccount, Account)) and fragment.service_name == 'GitHub':
            url = 'https://api.github.com/user/' + str(fragment.identifier)
            data = fetch_json(url, auth=self.token)
            if not data:
                return

            # TODO: fetch from https://api.github.com/users/xxxxxxx/events/public

            if 'id' not in data:
                print(id, data)
                return None

            return self.create_identity(data)
