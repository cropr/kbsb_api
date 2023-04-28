import asyncio
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from kbsb import settings
from kbsb.crud import get_db

from reddevil.service.sv_page import (
    updatePage,
)
from reddevil.models.md_page import (
    PageIn,
    PageUpdate,
    PageComponent,
)
from reddevil.crud.db_page import DbPage
from reddevil.models.md_i18nfield import I18nField

oldpages: list = []

async def main():
    """
    convert pages to new version
    """
    coll = get_db()['rd_page']
    for oldpage in oldpages:

        # check if it is an old page
        body, intro, title = process_locale(oldpage['page_i18n_fields'], oldpage['name'])
        expdate = oldpage['expired_ts'].get('$date')[0:10] if oldpage['expired_ts'] else ''
        pubdate = oldpage['published_ts'].get('$date')[0:10] if oldpage['published_ts'] else ''
        newpage = {
            'body': body,
            'component': oldpage['component'],
            'doctype': oldpage['doctype'],
            'enabled': oldpage['enabled'],
            'expirationdate':  expdate,
            'intro': intro,
            'languages': oldpage['languages'],
            'name': oldpage['name'],
            'owner': oldpage.get('owner', None),
            'publicationdate': pubdate,
            'slug': oldpage['slug'],
            'title': title,
            '_id': str(uuid.uuid4()),
            '_version': 2,
            '_documenttype': 'page',
            '_creationtime': datetime.fromisoformat(oldpage['created_ts']['$date'][:-1]),
            '_modificationtime': datetime.fromisoformat(oldpage['modified_ts']['$date'][:-1])
        }
        await coll.insert_one(newpage) 
        
def process_locale(i18n_fields, name):
    body = {'default': dict(value='')}
    intro = {'default': dict(value='')}
    title = {'default': dict(value=name)}
    for l in ('en', 'fr', 'de', 'nl'):
        if l in i18n_fields:
            body[l] = dict(value=i18n_fields[l].get('body', ''))
            intro[l] = dict(value=i18n_fields[l].get('intro', ''))
            title[l] = dict(value=i18n_fields[l].get('title', ''))
    return (body, intro, title)


if __name__ == '__main__':
    with open('share/data/pages_old.json', 'r') as fp:
        oldpages = json.load(fp)
    asyncio.run(main())
