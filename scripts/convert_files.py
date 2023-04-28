import asyncio
import json
import uuid
import os.path
from datetime import date, datetime, timedelta, timezone
from kbsb import settings
from kbsb.crud import get_db

from reddevil.service.sv_file import (
    updateFile,
)
from reddevil.models.md_file import (
    FileIn,
    FileDetailedIn,
)
from reddevil.crud.db_file import DbFile
from reddevil.models.md_i18nfield import I18nField


async def main(oldfiles):
    """
    convert files to new version
    """
    coll = get_db()['rd_file']
    for oldfile in oldfiles:

        # check if it is an old filefrom kbsb.settings import LOG_CONFIG
        topicdate = oldfile['topic_ts'].get('$date')[0:10] if oldfile.get('topic_ts') else ''
        newfile = {
            'archived': oldfile.get('archived', False),
            'created_by': oldfile.get('created_by', 'me'),
            'filelength': oldfile['filelength'],
            'locale': oldfile.get('locale', ''),
            'mimetype': oldfile['mimetype'],
            'name': oldfile['name'],
            'path': os.path.join(settings.FILESTORE, oldfile['url']),
            'topic': oldfile.get('topic', ''),
            'topicdate': topicdate,
            'url': oldfile['url'],
            '_id': str(uuid.uuid4()),
            '_version': 1,
            '_documenttype': 'file',
            '_creationtime': datetime.fromisoformat(oldfile['created_ts']['$date'][:-1]),
            '_modificationtime': datetime.fromisoformat(oldfile['modified_ts']['$date'][:-1])
        }
        await coll.insert_one(newfile) 
        
if __name__ == '__main__':
    with open('share/data/files_old.json', 'r') as fp:
        oldfiles = json.load(fp)
    asyncio.run(main(oldfiles))
