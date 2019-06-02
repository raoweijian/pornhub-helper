from flask_restful import Resource, request
from sqlalchemy.sql import func

from ..models import Task
from . import api
from .. import db
from flask import current_app


class TaskApi(Resource):
    def get(self, task_id):
        task = Task.query.get(task_id)
        return task.to_json()

    def put(self, task_id):
        task = Task.query.get(task_id)
        task.from_json(request.json)
        db.session.add(task)
        db.session.commit()
        return task.to_json()


class TaskListApi(Resource):
    page_size = 10

    def get(self):
        page = int(request.args.get('page', 1))
        offset = (page - 1) * self.page_size

        tasks = Task.query.filter(Task.status >= 0).limit(self.page_size).offset(offset).all()
        ret = {
            "data": [task.to_json() for task in tasks],
            "cur_page": page,
            "page_size": self.page_size,
            "task_count": self._get_task_count(),
        }
        return ret

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

    def _get_task_count(self):
        q = db.session.query(Task).filter(Task.status >= 0)
        count_q = q.statement.with_only_columns([func.count()])
        count = q.session.execute(count_q).scalar()
        return count


api.add_resource(TaskApi, '/tasks/<int:task_id>', endpoint='task')
api.add_resource(TaskListApi, '/tasks/', endpoint='tasks')
