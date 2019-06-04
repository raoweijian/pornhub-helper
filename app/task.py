import os
import re
import json
import requests
import urllib

from celery import Celery
from lxml import etree

from . import flask_app, db
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

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }

    s = requests.Session()
    resp = s.get(task.url, headers=headers)
    html = etree.HTML(resp.content)

    site = "pornhub"
    if task.url.startswith("https://www.xvideos.com"):
        site = "xvideos"

    # 获取视频标题
    title = get_title(html, site)

    # 更新任务标题和状态
    task.title = title
    task.status = 1
    db.session.add(task)
    db.session.commit()

    # 开始下载视频
    download_url = get_download_url(html, site)

    try:
        download(path, download_url, title, 'mp4')
        task.status = 2
    except Exception:
        print("download exception")
        task.status = -1
        pass

    db.session.add(task)
    db.session.commit()


def download(path, url, name, filetype):
    filepath = '%s/%s.%s' % (path, name, filetype)
    if os.path.exists(filepath):
        return
    urllib.request.urlretrieve(url, '%s' % filepath)


def get_download_url(html, site):
    if site == "xvideos":
        return html.cssselect("#html5video_base")[0].xpath("div//a")[-1].values()[1]
    elif site == "pornhub":
        js = html.xpath('//*[@id="player"]/script/text()')[0]
        tem = re.findall('var\\s+\\w+\\s+=\\s+(.*);\\s+var player_mp4_seek', js)[-1]
        con = json.loads(tem)
        for _dict in con['mediaDefinitions']:
            if 'quality' in _dict.keys() and _dict.get('videoUrl'):
                return _dict.get('videoUrl')


def get_title(html, site):
    if site == "xvideos":
        return html.cssselect("h2.page-title")[0].text.strip()
    elif site == "pornhub":
        return ''.join(html.xpath('//h1//text()')).strip()
