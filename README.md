# pornhub-helper
pornhub 下载工具，提供了 web ui
底层下载功能基于 [pornhub](https://github.com/formateddd/pornhub)

## 设计简介
做这个项目的初衷，是因为通过代理看网页还行，看视频太卡（可能是我买的代理网络环境太差了）。

整体的使用流程如下：
1. 打开 pornhub，找到自己喜欢的视频，复制该视频的地址
2. 把这个 app 部署到可以访问 pornhub 的机器上, 打开 web ui，把地址添加到下载任务里
3. 后台开始自动下载
4. 下载完成后，mp4 文件已经存储到了 app 所在的机器。如果想要再下载到本机，可以通过复制页面上提供的下载地址，用迅雷下载
5. 已经用迅雷下载到本地了，不需要在页面上展示出来的任务，可以点击确认，取消展示，让列表更清爽。

## 部署帮助 
### 配置 nginx
```
# 安装 nginx
yum install -y nginx

# 把项目需要的 nginx 配置文件拷过去
cp conf/pornhub-helper-nginx.conf /etc/nginx/conf.d/

# 重启 nginx
nginx -s reload
```
### 启动 web ui
```
# 安装虚拟环境
virtualenv venv
. venv/bin/active
pip install -r requirements.txt

# 启动 uwsgi
uwsgi --ini uwsgi/uwsgi.ini
```

### 启动 celery
```
nohup celery -A app.task.flask_celery worker --concurrency=4 > celery.out &
```

## 页面功能介绍
![图片](https://github.com/raoweijian/pornhub-helper/blob/master/png/usage.png)


## tips
1. 页面会自动刷新，无需手动刷。
2. 如果这个 app 是部署在本机的, 那么在页面提示下载完成后，可以直接去项目的 download 目录里找。
3. nginx, uwsgi 配置文件都默认项目是部署在 /root/pornhub-helper 目录下，如果实际部署目录不是这个，需要自行调整配置文件里的内容。
