import os
import re
import json
import requests
import urllib

from celery import Celery
from lxml import etree

from . import flask_app
from .models import Task


def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_celery = make_celery(flask_app)


@flask_celery.task
def download_video(task_id, path):
    task = Task.query.get(task_id)
    task.status = 1

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }

    print("start download url: %s" % task.url)
    s = requests.Session()
    resp = s.get(task.url, headers=headers)
    print("get html done")
    html = etree.HTML(resp.content)
    title = ''.join(html.xpath('//h1//text()')).strip()

    js = html.xpath('//*[@id="player"]/script/text()')[0]
    tem = re.findall('var\\s+\\w+\\s+=\\s+(.*);\\s+var player_mp4_seek', js)[-1]
    con = json.loads(tem)

    for _dict in con['mediaDefinitions']:
        if 'quality' in _dict.keys() and _dict.get('videoUrl'):
            try:
                download(path, _dict.get('videoUrl'), title, 'mp4')
                task.status = 2
                break
            except Exception:
                task.status = -1
                pass


def download(path, url, name, filetype):
    filepath = '%s/%s.%s' % (path, name, filetype)
    if os.path.exists(filepath):
        return
    urllib.request.urlretrieve(url, '%s' % filepath)
