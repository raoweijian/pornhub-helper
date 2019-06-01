from datetime import datetime

from . import db


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False, unique=True)
    title = db.Column(db.String(128), nullable=False, default="")
    status = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.now)
    modify_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __mapper_args__ = {
        "order_by": create_time.desc()
    }

    def to_json(self):
        ret = {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "status": self._status_desc(self.status),
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "modify_time": self.modify_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return ret

    def _status_desc(self, status):
        mapper = {
            0: "等待下载",
            1: "下载中",
            2: "下载完成",
            -1: "下载失败",
        }
        return mapper[status]
