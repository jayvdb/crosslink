from crosslink.service import Service

from crosslink.identifiers import *
from crosslink.utils import *


class KeybaseAccount(ServiceAccount):
    pass


class KeybaseIdentity(Identity):

    def __init__(self, provider, identifier,
                 preferred_username,
                 name,
                 current_location,
                 about_me,
                 email,
                 proofs,
                 ):
        super(KeybaseIdentity, self).__init__(provider, identifier)
        self.preferred_username = preferred_username
        self.name['formatted'] = name
        self.about_me = about_me
        self.current_location = current_location
        if email:
            self.emails.append(email)

        if proofs:
            for proof in proofs:
                proof_type = proof['proof_type']
                username = proof['nametag']
                assert proof['state'] == 1
                if proof_type == 'generic_web_site':
                    parts = username.split('.')
                    if 'gitlab' in parts:
                        proof_type = 'gitlab'
                        username = parts[0]
                    elif 'bitbucket' in parts:
                        proof_type = 'bitbucket'
                        username = parts[0]
                    else:
                        continue

                account = Account(str(proof_type), Username(username))
                self.accounts.append(VerifiedAccount(account, provider))


class KeybaseService(Service):

    name = 'Keybase'
    website = 'https://keybase.io/'

    _url = website + '_/api/1.0/user/lookup.json?{service}={value}'

    _account_cls = KeybaseAccount
    _identity_cls = KeybaseIdentity

    supported_services = ('GitHub', 'Twitter', 'Reddit', 'Hackernews', 'Facebook')
    pages_domain = ('GitLab', 'BitBucket', )

    all_services = set(supported_services) | set(pages_domain)

    def create_identity(self, data):
        email = None
        print(data.keys())
        if 'emails' in data and 'primary' in data['emails']:
            item = data['emails']['primary']
            is_verified = 'is_verified' in item and item['is_verified'] == 1
            email = Email(item['email'])
            if is_verified:
                email = VerifiedAccount(email, self)

        proofs = None
        if 'proofs_summary' in data and 'all' in data['proofs_summary']:
            proofs = data['proofs_summary']['all']

        i = KeybaseIdentity(
             provider=self, identifier=data['id'],
             preferred_username=data['basics']['username'],
             name=data['profile']['full_name'],
             current_location=data['profile']['location'],
             about_me=data['profile']['bio'],
             email=email,
             proofs=proofs,
        )
        return i

    def get_identity(self, fragment):
        if isinstance(fragment, Account) and isinstance(fragment.identifier, Username):
            url = None
            if fragment.service_name in self.supported_services:
                url = self._url.format(service=fragment.service_name.lower(),
                                       value=str(fragment.identifier))
            elif fragment.service_name.lower() == 'keybase':
                url = self._url.format(service='usernames',
                                       value=str(fragment.identifier))
            if url:
                data = fetch_json(url)

                assert 'status' in data
                assert 'name' in data['status']
                if data['status']['name'] != 'OK':
                    return None

                assert 'them' in data
                assert len(data['them']) >= 1

                entry = data['them'][0]

                return self.create_identity(entry)
