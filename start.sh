sudo nginx
sudo service redis-server start
uwsgi --ini uwsgi/uwsgi.ini
celery -A app.task.flask_celery worker --concurrency=4
