from apps import db
from sqlalchemy import func
import enum

class Product(db.Model):

    __tablename__ = 'Product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    info = db.Column(db.String(120), nullable=True)
    price = db.Column(db.Integer, nullable=True)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def get_list(cls):
        return cls.query.all()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'info': self.info,
            'price': self.price
        }
    
    @classmethod
    def get_json_list(cls):
        products = cls.query.all()
        return [product.to_dict() for product in products]
    

class StatusChoices(enum.Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RUNNING = 'RUNNING'


class TaskResult(db.Model):
    __tablename__ = 'TaskResult'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False)
    periodic_task_name = db.Column(db.String(255), nullable=True)
    task_name = db.Column(db.String(255), nullable=True)
    task_args = db.Column(db.Text, nullable=True)
    task_kwargs = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(StatusChoices), default=StatusChoices.PENDING)
    worker = db.Column(db.String(100), nullable=True)
    content_type = db.Column(db.String(128), nullable=False)
    content_encoding = db.Column(db.String(64), nullable=False)
    result = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_done = db.Column(db.DateTime, onupdate=func.now())
    traceback = db.Column(db.Text, nullable=True)

    def as_dict(self):
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'task_args': self.task_args,
            'task_kwargs': self.task_kwargs,
            'status': self.status,
            'result': self.result,
            'date_done': self.date_done,
            'traceback': self.traceback,
            'meta': self.meta,
            'worker': self.worker
        }

    def __repr__(self):
        return f'<TaskResult {self.id} - {self.task_id} ({self.status})>'