from flask_restful import Resource, request

from ..models import Task
from . import api
from .. import db
from flask import current_app


class TaskApi(Resource):
    def get(self, task_id):
        task = Task.query.get(task_id)
        return task.to_json()


class TaskListApi(Resource):
    def get(self):
        tasks = Task.query.all()
        for i in range(len(tasks)):
            tasks[i] = tasks[i].to_json()
        return tasks

    def post(self):
        if Task.query.filter_by(url=request.json["url"]).first():
            return "this url is already in task"

        task = Task()
        task.status = 0
        task.url = request.json["url"]
        db.session.add(task)
        db.session.commit()
        # 添加一个 celery 任务
        from ..task import download_video
        download_video.delay(task.id, current_app.config["DOWNLOAD_PATH"])

        return "ok"


api.add_resource(TaskApi, '/tasks/<int:article_id>', endpoint='task')
api.add_resource(TaskListApi, '/tasks/', endpoint='tasks')
