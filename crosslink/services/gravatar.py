from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class GravatarAccount(ServiceAccount):
    pass


class GravatarIdentity(Identity):

    def __init__(self, provider, identifier,
                 name,
                 preferred_username,
                 display_name,
                 about_me,
                 primary_hash,
                 request_hash,
                 current_location,
                 emails,
                 ims,
                 accounts,
                 urls,
                 phone_numbers,
                 profile_background,
                 photos,
                 ):
        super(GravatarIdentity, self).__init__(provider, identifier)
        self.preferred_username = preferred_username

        if isinstance(name, dict):
            self.name.update(name)
        else:
            assert not name

        self.about_me = about_me
        self.current_location = current_location

        self._phone_numbers = phone_numbers
        self._profile_background = profile_background
        self._photos = photos

        account = GravatarAccount(provider, GravatarMD5Hash(primary_hash))
        self.emails.append(VerifiedAccount(account, provider))

        if request_hash and request_hash != primary_hash:
            account = GravatarAccount(provider, GravatarMD5Hash(request_hash))
            self.emails.append(VerifiedAccount(account, provider))

        # All emails are verified
        if emails:
            assert isinstance(emails, list)
            assert len(emails) >= 1
            for email in emails:
                assert isinstance(email, dict)
                obj = VerifiedAccount(Email(email['value']), provider)
                self.emails.append(obj)
                if email.get('primary') == 'true':
                    self.primary_email = obj

        if ims:
            assert isinstance(ims, list)
            assert len(ims) >= 1
            for im in ims:
                assert isinstance(im, dict)
                self.ims.append(Account(str(im['type']), Username(str(im['value']))))

        if accounts:
            assert isinstance(accounts, list)
            assert len(accounts) >= 1
            for account in accounts:
                assert isinstance(account, dict)
                userid = account.get('userid')
                if not userid:
                    userid = account.get('username')
                if not userid:
                    print(account)
                    assert False
                self.accounts.append(Account(str(account['shortname']), Username(userid)))

        if urls:
            for url in urls:
                if url['value'] not in ('https://github.com', ):
                    # url['title'] is not being used
                    self.urls.append(Account('web', Webpage(str(url['value']))))


class GravatarService(Service):

    name = 'Gravatar'
    website = 'https://www.gravatar.com/'

    _url = website + '{value}.json'

    _can_resolve = [GravatarMD5Hash]
    _can_verify = [GravatarMD5Hash]
    _account_cls = GravatarAccount
    _identity_cls = GravatarIdentity

    def create_identity(self, data):
        entry = data

        assert 'hash' in entry

        request_hash = None

        if entry['hash'] != entry['requestHash']:
            request_hash = entry['requestHash']

        assert entry['thumbnailUrl'] == 'https://secure.gravatar.com/avatar/' + entry['hash']

        i = GravatarIdentity(
             provider=self, identifier=entry['id'],
             preferred_username=entry.get('preferredUsername'),
             name=entry.get('name'),
             display_name=entry.get('displayName'),
             about_me=entry.get('aboutMe'),
             primary_hash=entry['hash'],
             request_hash=request_hash,
             current_location=entry.get('currentLocation'),
             emails=entry.get('emails'),
             ims=entry.get('ims'),
             accounts=entry.get('accounts'),
             urls=entry.get('urls'),
             phone_numbers=entry.get('phoneNumbers'),
             profile_background=entry.get('profileBackground'),
             photos=entry.get('photos'),
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, GravatarMD5Hash):
            url = self._url.format(value=fragment.value)
            data = fetch_json(url)
            if not data:
                return

            assert isinstance(data, dict)
            assert 'entry' in data
            assert len(data) == 1
            assert len(data['entry']) == 1
            entry = data['entry'][0]

            return self.create_identity(entry)
