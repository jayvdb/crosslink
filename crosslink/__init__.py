from __future__ import print_function

__version__ = '0.2.0'

import os
import sys

from crosslink.identifiers import *
from crosslink.service import Service
from crosslink.services import *

services = [
    OriginService,
    GravatarHashService,
    OpenHubService,
    GravatarService,
    LibravatarService,
    GitLabService,
    GitHubService,
    KeybaseService,
]


def get_services(names=None):
    if isinstance(names, str):
        names = [names]

    loaded = []
    for service in services:
        name = service.name
        if names and name not in names:
            continue
        env = 'CROSSLINK_%s_TOKEN' % name.upper()
        token = os.getenv(env, None)
        if token and ':' in token:
            token = tuple(token.split(':', 1))
        try:
            loaded.append(service(token=token))
        except Exception as e:
            print('Failed to load %s: %s' % (name, e), file=sys.stderr)

    return loaded


def resolve(haves, services):
    if not isinstance(haves, list):
        haves = [haves]

    not_processed = haves[:]

    while not_processed:
        current = not_processed.pop()
        if isinstance(current, Account):
            current_item = current
        elif isinstance(current, VerifiedAccount):
            current_item = current.account
        else:
            current_item = current
        for service in services:
            new = service.get_identity(current_item)
            if new:
                if new not in haves:
                    haves.append(new)
                    not_processed.append(new)
                if hasattr(new, 'get_fragments'):
                    for item in new.get_fragments():
                        if item not in haves:
                            haves.append(item)
                            not_processed.append(item)

    return haves


def need(haves, want, services):
    results = resolve(haves, services)
    for item in results:
        if isinstance(item, want):
            return item
        if isinstance(item, VerifiedAccount):
            item = item.account
            print(item.__class__, item)
            if isinstance(item, want):
                return item
        if isinstance(item, Account):
            item = item.identifier
            if isinstance(item, want):
                return item

    print(results)
