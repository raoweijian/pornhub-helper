import os
import re
import json
import requests
import urllib
import js2py

from celery import Celery
from lxml import etree
from clint.textui import progress

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
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}


@flask_celery.task
def download_video(task_id, path):
    task = Task.query.get(task_id)

    # s = requests.Session()
    print("try to download %s" % task.url)
    resp = requests.get(task.url, headers=headers, verify=False)
    print("get base html done")
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
        db.session.add(task)
    except Exception as e:
        print(e)
        print("download exception")
        # task.status = -1
        db.session.delete(task)
        pass
    db.session.commit()


def get_download_url(html, site):
    if site == "xvideos":
        return html.cssselect("#html5video_base")[0].xpath("div//a")[-1].values()[1]
    elif site == "pornhub":
        js_temp = html.xpath('//script/text()')
        for j in js_temp:
            if 'flashvars' in j:
                js = ''.join(j.split('\n')[:-8])
                videoUrl = exeJs(js)
                return videoUrl


def download(path, url, name, filetype):
    filepath = '%s/%s.%s' % (path, name, filetype)
    if os.path.exists(filepath):
        return

    response = requests.get(url, headers=headers, stream=True)
    with open(filepath, "wb") as fp:
        total_length = int(response.headers.get('content-length'))
        for ch in progress.bar(response.iter_content(chunk_size=2391975), expected_size=(total_length / 1024) + 1):
            if ch:
                fp.write(ch)
    print('download success :: %s' % filepath)


def get_title(html, site):
    if site == "xvideos":
        return html.cssselect("h2.page-title")[0].text.strip()
    elif site == "pornhub":
        return ''.join(html.xpath('//h1//text()')).strip()


def exeJs(js):
    flashvars = re.findall('flashvars_\d+', js)[0]
    res = js2py.eval_js(js + flashvars)
    if res.quality_720p:
        return res.quality_720p
    elif res.quality_480p:
        return res.quality_480p
    elif res.quality_240p:
        return res.quality_240p
    else:
        print('parse url error')
