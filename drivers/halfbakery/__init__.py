import requests
import feedparser

def login(username, password):
    '''
    -> store session locally in '~/.metaform'
    -> store encrypted credentials with data in github, to use as link.
    '''
    print('performing login...')
    pass

def sync_one(url):
    '''
    -> Download a single item content with comments.
    '''
    pass

def sync_all(page_size=100, offset=0, limit=None, sync_comments=False):
    '''
    -> Download all titles, descriptions and dates.
    -> Create if not exists, update if exists. (call sync_one if updated)
    -> produce (yield) items with *, +, -.
    '''

    feed_url = 'http://www.halfbakery.com/lr/view/fxc=230:s=R:d=iwqhvroc:do={offset}:dn={page_size}:ds=A:n=tiny:t=halfbakery'

    while True:

        results = feedparser.parse(feed_url.format(
            page_size=page_size,
            offset=offset
        ))['entries']

        for result in results:
            result['-'] = result['id']
            yield result

        if len(results) < page_size:
            break

        offset += page_size

        if limit:
            if offset >= limit:
                break


def harvest(limit=None):

    authenticate = input('Do you want to login and bind encrypted login info? [y/N] ')

    if authenticate in ['y', 'Y']:
        login()

    complete = input('Do you want to synchronize comments? Takes much time. [y/N] ')

    if complete in ['y', 'Y']:
        complete = True
    else:
        complete = False


    for item in sync_all(sync_comments=complete, limit=limit):
        yield item
