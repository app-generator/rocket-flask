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

    def __str__(self):
        return str(self.value)


class TaskResult(db.Model):
    __tablename__ = 'TaskResult'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=True)
    periodic_task_name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(StatusChoices), default=StatusChoices.PENDING)
    result = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_done = db.Column(db.DateTime, nullable=True)