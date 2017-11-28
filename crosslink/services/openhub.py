from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class OpenHubAccount(ServiceAccount):
    pass


class OpenHubIdentityLanguage():
    def __init__(self, color, name, experience_months,
                 total_commits, total_lines_changed, comment_ratio):
        self.color = color
        self.name = name
        self.experience_months = experience_months
        self.total_commits = total_commits
        self.total_lines_changed = total_lines_changed
        self.comment_ratio = comment_ratio


class OpenHubBadge():
    def __init__(self, name, level, description, image_url, pips_url):
        self.name = name
        self.level = level
        self.description = description
        self.image_url = image_url
        self.pips_url = pips_url


class OpenHubIdentity(Identity):

    def __init__(self, provider, identifier,
                 preferred_username,
                 name,
                 about_me,
                 created_at,  # unused
                 updated_at,  # unused
                 homepage_url,
                 twitter_account,
                 avatar_url,
                 email_sha1,
                 posts_count,
                 location,
                 country_code,
                 latitude, longitude,
                 kudo_score,
                 languages,  # OpenHubIdentityLanguage
                 badges,  # OpenHubIdentityBadge
                 extras=None,
                 ):
        super(OpenHubIdentity, self).__init__(provider, identifier)
        self.preferred_username = preferred_username

        self._created_at = created_at
        self._updated_at = updated_at

        self.name['formatted'] = name
        self.about_me = about_me
        self.current_location = location

        if homepage_url:
            self.urls.append(Webpage(homepage_url))
        if twitter_account:
            self.urls.append(Account('twitter', Username(twitter_account)))

        gravatar_prefix, gravatar_hash = avatar_url.split('=', 1)
        assert gravatar_prefix == 'http://www.gravatar.com/avatar.php?gravatar_id'
        account = Account('gravatar', GravatarMD5Hash(gravatar_hash))
        self.emails.append(VerifiedAccount(account, provider))

        self.emails.append(EmailSHA1(email_sha1))

        self._posts_count = posts_count
        self._country_code = country_code
        self._latitude = latitude
        self._longitude = longitude
        self._kudo_score = kudo_score
        # TODO: languages & badges


class OpenHubService(Service):

    name = 'OpenHub'
    website = 'https://www.openhub.net/'

    _url = website + 'accounts/{value}.xml?api_key={token}'

    _can_resolve = [GravatarMD5Hash]
    _can_verify = [GravatarMD5Hash]
    _account_cls = OpenHubAccount
    _identity_cls = OpenHubIdentity

    def create_identity(self, data, extras=None):
        i = OpenHubIdentity(
             provider=self, identifier=data['id'],
             preferred_username=data['login'],
             name=data['name'],
             about_me=data['about'],
             created_at=data['created_at'],
             updated_at=data['updated_at'],
             homepage_url=data['homepage_url'],
             twitter_account=data['twitter_account'],
             avatar_url=data['avatar_url'],
             email_sha1=data['email_sha1'],
             posts_count=data['posts_count'],
             location=data['location'],
             country_code=data['country_code'],
             latitude=data['latitude'],
             longitude=data['longitude'],
             kudo_score=data.get('kudo_score'),
             languages=data.get('languages'),
             badges=data['badges'],
             extras=extras,
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, GravatarMD5Hash):
            url = self._url.format(value=fragment.value, token=self.token)
            data = fetch_xml(url)
            if not data:
                return

            if 'response' in data and 'result' in data['response']:
                entry = data['response']['result']['account']
                account = Account('gravatar', fragment)
                extras = [VerifiedAccount(account, self)]
                return self.create_identity(entry, extras)
